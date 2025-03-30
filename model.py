import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import onnx
import onnxruntime

class Classifier:
    def __init__(self, num_classes=4, device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model(num_classes)
        self.model.to(self.device)
        self.train_dataset = None  # 儲存 train_dataset 以便後續使用

    def _build_model(self, num_classes):
        model = models.resnet18(pretrained=True)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model

    def train(self, train_dir, val_dir, epochs=10, batch_size=32, lr=0.001):
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        self.train_dataset = datasets.ImageFolder(train_dir, transform=transform)
        val_dataset = datasets.ImageFolder(val_dir, transform=transform)

        train_loader = DataLoader(self.train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)

        for epoch in range(epochs):
            self.model.train()
            running_loss = 0.0
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()

            print(f"Epoch {epoch+1}/{epochs}, Loss: {running_loss/len(train_loader):.4f}")
            self._validate(val_loader)

    def _validate(self, val_loader):
        self.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                _, preds = torch.max(outputs, 1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)

        print(f"Validation Accuracy: {correct/total:.4f}")

    def inference(self, image_path):
        from PIL import Image
        self.model.eval()

        idx_to_class = {v: k for k, v in self.train_dataset.class_to_idx.items()} if self.train_dataset else None

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        image = Image.open(image_path).convert("RGB")
        input_tensor = transform(image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            outputs = self.model(input_tensor)
            _, preds = torch.max(outputs, 1)

        return idx_to_class[preds.item()] if idx_to_class else preds.item()

    def save_model(self, file_path):
        torch.save(self.model.state_dict(), file_path)
        print(f"Model saved to {file_path}")

    def load_model(self, file_path):
        self.model.load_state_dict(torch.load(file_path, map_location=self.device))
        self.model.to(self.device)
        print(f"Model loaded from {file_path}")

    def export_to_onnx(self, onnx_path, input_size=(1, 3, 224, 224)):
        dummy_input = torch.randn(*input_size).to(self.device)
        torch.onnx.export(
            self.model, 
            dummy_input, 
            onnx_path, 
            export_params=True, 
            opset_version=11, 
            input_names=['input'], 
            output_names=['output']
        )
        print(f"Model exported to {onnx_path}")

    def onnx_inference(self, onnx_path, image_path):
        from PIL import Image
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        image = Image.open(image_path).convert("RGB")
        input_tensor = transform(image).unsqueeze(0).numpy()

        # 使用 ONNX Runtime 進行推論
        ort_session = onnxruntime.InferenceSession(onnx_path)
        ort_inputs = {ort_session.get_inputs()[0].name: input_tensor}
        ort_outs = ort_session.run(None, ort_inputs)
        prediction = ort_outs[0].argmax(axis=1)[0]

        idx_to_class = {v: k for k, v in self.train_dataset.class_to_idx.items()} if self.train_dataset else None
        return idx_to_class[prediction] if idx_to_class else prediction

# 使用方式
classifier = Classifier(num_classes=4)
# classifier.train(train_dir="path_to_train", val_dir="path_to_val", epochs=10)
# classifier.export_to_onnx("model.onnx")
result = classifier.onnx_inference("model.onnx", "path_to_image")
print("Predicted label:", result)
