import threading
import time
import socket
from queue import Queue
import cv2
import sys
import keyboard
from USBCamera import USBCamera
from ONNXClassifier import ONNXClassifier

# Server 配置
HOST = "192.168.12.98"  # 與你的client檔案一致
PORT = 65432

class MainApplication:
    def __init__(self):
        # 初始化相機
        self.camera = USBCamera(camera_index=2)
        self.running = False
        
        # 初始化ONNX模型
        class_mapping = {0: "bottle", 1: "glass_bottle", 2: "iron", 3: "paper"}
        self.classifier = ONNXClassifier("model.onnx", class_mapping)
        
        # Socket客戶端
        self.socket = None
        self.connect_to_server()
        
        # 用於保存圖片的隊列
        self.save_queue = Queue()
        
    def connect_to_server(self):
        """連接到server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Connecting to {HOST}:{PORT}...")
            self.socket.connect((HOST, PORT))
            print("Connected to server")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            sys.exit(1)

    def send_to_server(self, message):
        """發送消息到server"""
        try:
            self.socket.sendall(message.encode('utf-8'))
            print(f"Sent to server: {message}")
        except Exception as e:
            print(f"Error sending to server: {e}")

    def capture_and_process(self):
        """處理圖片擷取和模型預測"""
        while self.running:
            if keyboard.is_pressed('enter'):
                # 儲存當前畫面
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"
                self.camera.request_save(filename)
                
                # 等待圖片保存完成
                time.sleep(0.5)
                
                # 使用模型進行預測
                prediction = self.classifier.predict(filename)
                print(f"Model prediction: {prediction}")
                
                # 將結果發送到server
                self.send_to_server(f"Prediction: {prediction}")
                
                # 防止連續觸發
                time.sleep(0.5)
            time.sleep(0.01)

    def start(self):
        """啟動應用程式"""
        self.running = True
        self.camera.start()
        
        # 啟動處理線程
        process_thread = threading.Thread(target=self.capture_and_process)
        process_thread.daemon = True
        process_thread.start()
        
        print("Application started. Press Enter to capture and classify, Ctrl+C to exit")

    def stop(self):
        """停止應用程式"""
        self.running = False
        self.camera.stop()
        if self.socket:
            self.socket.close()
        print("Application stopped")

def main():
    app = MainApplication()
    try:
        app.start()
        while True:
            time.sleep(1)  # 主線程保持運行
    except KeyboardInterrupt:
        print("\nShutting down...")
        app.stop()
    except Exception as e:
        print(f"Error: {e}")
        app.stop()

if __name__ == "__main__":
    main()