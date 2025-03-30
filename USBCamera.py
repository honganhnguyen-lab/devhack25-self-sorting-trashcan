import cv2
import threading
import time
from queue import Queue

class USBCamera:
    def __init__(self, camera_index=2):
        """Initialize the camera with a specified camera index"""
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)  # Use DirectShow backend
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.running = False
        self.frame = None
        self.frame_lock = threading.Lock()
        self.save_queue = Queue()
        
        if not self.cap.isOpened():
            raise Exception(f"Failed to open USB camera (index {self.camera_index})")

    def start(self):
        """Start the camera and begin multi-threaded operation"""
        if not self.running:
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.save_thread = threading.Thread(target=self._save_loop)
            self.capture_thread.daemon = True
            self.save_thread.daemon = True
            self.capture_thread.start()
            self.save_thread.start()
            print("Camera started")

    def _capture_loop(self):
        """Thread to continuously capture frames"""
        max_retries = 10
        retry_count = 0
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture image, retrying...")
                retry_count += 1
                if retry_count >= max_retries:
                    print("Max retries reached, stopping camera...")
                    self.running = False
                    break
                time.sleep(0.1)
                continue
            
            retry_count = 0
            with self.frame_lock:
                self.frame = frame.copy()
            time.sleep(0.1)  # Reduced to ~10 FPS

    def _save_loop(self):
        """Thread to handle save requests"""
        while self.running:
            if not self.save_queue.empty():
                filename = self.save_queue.get()
                self.save_current_frame(filename)
            time.sleep(0.01)

    def save_current_frame(self, filename='capture.jpg'):
        """Save the current frame to a specified file"""
        with self.frame_lock:
            if self.frame is not None:
                cv2.imwrite(filename, self.frame)
                print(f"Image saved as {filename}")
            else:
                print("No frame available to save")

    def request_save(self, filename='capture.jpg'):
        """Request to save the current frame from an external call"""
        self.save_queue.put(filename)

    def detect_and_draw_objects(self, frame):
        """Detect objects in the frame and draw bounding boxes"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame

    def get_current_frame(self):
        """Get the current frame with lock protection"""
        with self.frame_lock:
            if self.frame is not None:
                return self.frame.copy()
        return None

    def stop(self):
        """Stop the camera and release resources"""
        self.running = False
        self.capture_thread.join()
        self.save_thread.join()
        self.cap.release()
        print("Camera stopped")

if __name__ == "__main__":
    try:
        camera = USBCamera(camera_index=2)
        camera.start()
        time.sleep(2)
        camera.request_save("image1.jpg")
        time.sleep(1)
        camera.request_save("image2.jpg")
        frame = camera.get_current_frame()
        if frame is not None:
            processed_frame = camera.detect_and_draw_objects(frame)
            cv2.imwrite("processed_image.jpg", processed_frame)
            print("Processed image saved as processed_image.jpg")
        time.sleep(2)
        camera.stop()
    except Exception as e:
        print(e)