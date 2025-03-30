import onnxruntime
import numpy as np
from PIL import Image

class ONNXClassifier:
    def __init__(self, onnx_model_path, class_mapping=None):
        self.session = onnxruntime.InferenceSession(onnx_model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.class_mapping = class_mapping

    def preprocess_image(self, image_path):
        # 圖像預處理：調整大小、轉換為 numpy
        image = Image.open(image_path).convert("RGB").resize((224, 224))
        image_np = np.array(image).astype('float32') / 255.0  # 將類型設為 float32
        # 正規化數據
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)  # 確保均值和標準差類型一致
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        image_np = (image_np - mean) / std
        # HWC -> CHW 格式調整
        image_np = np.transpose(image_np, (2, 0, 1))
        # 增加一個 batch 維度
        return np.expand_dims(image_np, axis=0)

    def predict(self, image_path):
        # 預測結果
        image_tensor = self.preprocess_image(image_path)
        outputs = self.session.run(None, {self.input_name: image_tensor})
        predicted_class = np.argmax(outputs[0], axis=1)[0]
        if self.class_mapping:
            return self.class_mapping.get(predicted_class, f"Class {predicted_class}")
        return f"Class {predicted_class}"

if __name__ == "__main__":
    onnx_model_path = "model.onnx"
    image_path = "image1.jpg"

    class_mapping = {0: "bottle", 1: "glass_bottle", 2: "iron", 3: "paper"}

    classifier = ONNXClassifier(onnx_model_path, class_mapping)

    prediction = classifier.predict(image_path)
    print(f"Predicted Label: {prediction}")
