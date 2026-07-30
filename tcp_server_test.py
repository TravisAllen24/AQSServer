import socket
import threading
import time

HOST = "0.0.0.0"
PORT = 5000

def handle_client(conn, addr):
    print(f"Connected: {addr}")
    try:
        while True:
            message = f"$AQS,2026-07-19 18:56:48,27.18,32.82086,9.43,773,31269,178,23530,1,2,1,0\n"
            conn.sendall(message.encode())
            time.sleep(1)  # 1 Hz
    except (BrokenPipeError, ConnectionResetError):
        print(f"Disconnected: {addr}")
    finally:
        conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Listening on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server")
    finally:
        server.close()

if __name__ == "__main__":
    main()