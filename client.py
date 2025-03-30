import socket
import threading
import time

HOST = "192.168.12.98" 
PORT = 65432   

def receive_messages(sock):
    """Continuously receive and display messages from the server."""
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                print("Server disconnected")
                break
            print(f"\nServer: {data.decode('utf-8')}")
            print("Enter message: ", end='', flush=True)
    except Exception as e:
        print(f"Error receiving: {e}")
    finally:
        sock.close()
        print("Connection closed")

def start_client():
    try:
        # Create a socket and connect to the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"Connecting to {HOST}:{PORT}...")
        s.connect((HOST, PORT))
        print("Connected to server")
        
        # Start a thread to handle incoming messages
        receive_thread = threading.Thread(target=receive_messages, args=(s,))
        receive_thread.daemon = True
        receive_thread.start()
        
        # Main loop for sending messages
        try:
            while True:
                message = input("Enter message: ")
                if message.lower() == 'exit':
                    break
                s.sendall(message.encode('utf-8'))
                time.sleep(0.1)  # Small delay to avoid mixing output with incoming messages
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            s.close()
            
    except ConnectionRefusedError:
        print(f"Connection to {HOST}:{PORT} refused. Is the server running?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_client()
