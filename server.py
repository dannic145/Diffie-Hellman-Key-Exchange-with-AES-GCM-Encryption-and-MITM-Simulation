import socket
import json
import math
import hashlib
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM 

def is_prime(p):
    if p <= 1:
        return False
    if p <= 3:
        return True
    if p % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(p)) + 1, 2):
        if p % i == 0:
            return False
    return True


def derive_key(shared_secret):
    return hashlib.sha256(str(shared_secret).encode()).digest()


HOST = '127.0.0.1'
PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print("Server listening...")

    conn, addr = s.accept()
    with conn:
        print("Connected by", addr)

        data = json.loads(conn.recv(4096).decode())
        p = data["p"]
        g = data["g"]
        A = data["A"]

        if not is_prime(p):
            print("Received non-prime p. Closing connection.")
            conn.close()
            exit()

        b = 6
        B = pow(g, b, p)

        conn.sendall(json.dumps({"B": B}).encode())

        shared_secret = pow(A, b, p)
        aes_key = derive_key(shared_secret)
        aesgcm = AESGCM(aes_key)

        enc_data = json.loads(conn.recv(4096).decode())
        nonce = bytes.fromhex(enc_data["nonce"])
        ciphertext = bytes.fromhex(enc_data["ciphertext"])

        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        x, y = map(int, plaintext.decode().split(","))

        print(f"Server decrypted numbers: {x}, {y}")

        result = x * y

        nonce2 = os.urandom(12)
        encrypted_result = aesgcm.encrypt(nonce2, str(result).encode(), None)

        conn.sendall(json.dumps({
            "nonce": nonce2.hex(),
            "ciphertext": encrypted_result.hex()
        }).encode())
