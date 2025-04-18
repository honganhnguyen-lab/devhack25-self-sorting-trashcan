import socket
import threading
import time
from queue import Queue
import cv2
import keyboard
from USBCamera import USBCamera
from ONNXClassifier import ONNXClassifier

HOST = "192.168.12.98" 
PORT = 65432

class CameraClient:
    def __init__(self):
        self.camera = USBCamera(camera_index=2)
        self.running = False
        
        self.class_mapping = {0: "bottle", 1: "glass_bottle", 2: "iron", 3: "paper"}

        self.classifier = ONNXClassifier("model.onnx", self.class_mapping)
        
        self.socket = None
        
        self.save_queue = Queue()

    def receive_messages(self, sock):
        try:
            while self.running:
                data = sock.recv(1024)
                if not data:
                    print("Server disconnected")
                    break
                print(f"\nServer: {data.decode('utf-8')}")
        except Exception as e:
            print(f"Error receiving: {e}")
        finally:
            sock.close()
            print("Connection closed")

    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Connecting to {HOST}:{PORT}...")
            self.socket.connect((HOST, PORT))
            print("Connected to server")
            
            receive_thread = threading.Thread(target=self.receive_messages, args=(self.socket,))
            receive_thread.daemon = True
            receive_thread.start()
            return True
        except ConnectionRefusedError:
            print(f"Connection to {HOST}:{PORT} refused. Is the server running?")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

    def send_to_server(self, message):
        try:
            self.socket.sendall(message.encode('utf-8'))
            print(f"Sent to server: {message}")
        except Exception as e:
            print(f"Error sending to server: {e}")

    def capture_and_process(self):
        while self.running:
            if keyboard.is_pressed('enter'):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.jpg"
                self.camera.request_save(filename)
                
                time.sleep(0.5)
                
                prediction = self.classifier.predict(filename)
                print(f"Model prediction: {prediction}")

                keys = [key for key, value in self.class_mapping.items() if value == prediction]
                
                self.send_to_server(f"{keys[0]+1}")
                
                time.sleep(0.5)
            time.sleep(0.01)

    def start(self):
        self.running = True
        self.camera.start()
        
        if not self.connect_to_server():
            self.stop()
            return
        
        process_thread = threading.Thread(target=self.capture_and_process)
        process_thread.daemon = True
        process_thread.start()
        
        print("Client started. Press Enter to capture and classify, Ctrl+C to exit")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            self.stop()

    def stop(self):
        self.running = False
        self.camera.stop()
        if self.socket:
            self.socket.close()
        print("Client stopped")

if __name__ == "__main__":
    client = CameraClient()
    client.start()