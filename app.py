from flask import Flask, render_template, Response, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
from queue import Queue
import cv2
import socket
import os
from USBCamera import USBCamera
from ONNXClassifier import ONNXClassifier

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # 用於 WebSocket 的密鑰
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化相機和模型
camera = USBCamera(camera_index=2)
class_mapping = {0: "bottle", 1: "glass_bottle", 2: "iron", 3: "paper"}
classifier = ONNXClassifier("model.onnx", class_mapping)
latest_prediction = {"prediction": "None yet"}  # 儲存最新的預測結果
latest_captured_image = None  # 儲存最新的擷取影像
frame_lock = threading.Lock()  # 用於保護共享資源

# Socket 客戶端配置
HOST = "192.168.12.98"
PORT = 65432
socket_client = None
socket_thread = None
socket_running = True

# 確保 static/captures 資料夾存在
CAPTURE_DIR = "static/captures"
if not os.path.exists(CAPTURE_DIR):
    os.makedirs(CAPTURE_DIR)

def connect_to_socket_server():
    """連接到 socket server 並處理接收訊息"""
    global socket_client, socket_running
    while socket_running:
        try:
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.connect((HOST, PORT))
            print(f"Connected to socket server at {HOST}:{PORT}")
            
            # 持續接收 server 的訊息
            while socket_running:
                data = socket_client.recv(1024)
                if not data:
                    print("Socket server disconnected")
                    break
                message = data.decode('utf-8')
                print(f"Received from socket server: {message}")
                # 將接收到的訊息發送到前端
                socketio.emit('server_message', {'message': message}, namespace='/')
        except Exception as e:
            print(f"Socket error: {e}")
            socket_client.close()
            time.sleep(5)  # 斷線後等待 5 秒再重連
        finally:
            if socket_client:
                socket_client.close()

def send_to_socket_server(message):
    """發送訊息到 socket server"""
    try:
        socket_client.sendall(message.encode('utf-8'))
        print(f"Sent to socket server: {message}")
    except Exception as e:
        print(f"Error sending to socket server: {e}")

def generate_frames():
    """生成即時畫面串流"""
    camera.start()
    while True:
        frame = camera.get_current_frame()
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.1)  # 控制幀率

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    """擷取當前畫面並進行預測"""
    global latest_prediction, latest_captured_image
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{CAPTURE_DIR}/capture_{timestamp}.jpg"
    
    # 儲存當前畫面
    camera.request_save(filename)
    time.sleep(0.5)  # 等待圖片保存完成
    
    # 使用模型進行預測
    prediction = classifier.predict(filename)
    
    # 更新全局變數
    with frame_lock:
        latest_prediction = {"prediction": prediction}
        latest_captured_image = filename
    
    # 發送到 socket server
    keys = [key for key, value in class_mapping.items() if value == prediction] 
    send_to_socket_server(f"{keys[0]+1}")
    print("test_socket_out:",keys[0]+1)
    
    # 通過 WebSocket 發送到前端
    socketio.emit('prediction_update', latest_prediction, namespace='/')
    
    return jsonify(latest_prediction)

@app.route('/get_prediction')
def get_prediction():
    """返回最新的預測結果"""
    with frame_lock:
        return jsonify(latest_prediction)

@app.route('/get_captured_image')
def get_captured_image():
    """返回最新擷取的影像路徑"""
    with frame_lock:
        return jsonify({"image_path": latest_captured_image if latest_captured_image else ""})

@app.route('/')
def index():
    return render_template('index.html')

def shutdown():
    """關閉應用時清理資源"""
    global socket_running
    socket_running = False
    camera.stop()
    if socket_client:
        socket_client.close()
    print("Application shutting down...")

if __name__ == "__main__":
    # 啟動 socket 客戶端線程
    socket_thread = threading.Thread(target=connect_to_socket_server)
    socket_thread.daemon = True
    socket_thread.start()
    
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    finally:
        shutdown()