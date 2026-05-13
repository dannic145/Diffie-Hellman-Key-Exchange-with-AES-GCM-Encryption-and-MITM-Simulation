import socket
import threading

CLIENT_PORT = 6000        
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5000

def forward(src, dst, direction):

    try:
        while True:

            data = src.recv(4096)

            if not data:
                break

            print(f"\n[INTRUDER] Intercepted {direction}:")
            print(data.decode(errors="ignore"))

            dst.sendall(data)

    except ConnectionAbortedError:
        print(f"\n[INTRUDER] Connection aborted in {direction}")

    except ConnectionResetError:
        print(f"\n[INTRUDER] Connection reset in {direction}")

    finally:
        src.close()
        dst.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
    listener.bind(('127.0.0.1', CLIENT_PORT))
    listener.listen(1)
    print("[INTRUDER] Listening for client...")

    client_socket, addr = listener.accept()
    print("[INTRUDER] Client connected")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((SERVER_HOST, SERVER_PORT))
    print("[INTRUDER] Connected to real server")

    threading.Thread(
        target=forward,
        args=(client_socket, server_socket, "Client → Server")
    ).start()

    threading.Thread(
        target=forward,
        args=(server_socket, client_socket, "Server → Client")
    ).start()
