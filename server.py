import socket
import threading

HOST = "0.0.0.0"  
PORT = 65432 

def handle_client(conn, addr):
    """Handle an individual client connection."""
    print(f"New connection from {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
                
            message = data.decode('utf-8')
            print(f"Received from {addr}: {message}")
            
            conn.sendall(f"Server received: {message}".encode('utf-8'))
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection with {addr} closed")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        
        try:
            while True:
                conn, addr = s.accept()
                
                client_thread = threading.Thread(target=handle_client, args=(conn, addr))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            s.close()

if __name__ == "__main__":
    start_server()
