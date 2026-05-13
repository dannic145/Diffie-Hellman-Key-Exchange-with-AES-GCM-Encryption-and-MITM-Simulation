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


def prime_factors(n):
    factors = set()
    while n % 2 == 0:
        factors.add(2)
        n //= 2
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        while n % i == 0:
            factors.add(i)
            n //= i
    if n > 2:
        factors.add(n)
    return factors


def find_generator(p):
    phi = p - 1
    factors = prime_factors(phi)

    for g in range(2, p):
        valid = True
        for q in factors:
            if pow(g, phi // q, p) == 1:
                valid = False
                break
        if valid:
            return g
    return None


def derive_key(shared_secret):
    return hashlib.sha256(str(shared_secret).encode()).digest()


HOST = '127.0.0.1'
PORT = 6000

p = int(input("Enter a prime number p: "))

if not is_prime(p):
    print(" p is not prime. Exiting.")
    exit()

g = find_generator(p)
print(f"Prime p verified: {p}")
print(f"Generator g found: {g}")

a = 15
A = pow(g, a, p)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    s.sendall(json.dumps({
        "p": p,
        "g": g,
        "A": A
    }).encode())

    B = json.loads(s.recv(1024).decode())["B"]

    shared_secret = pow(B, a, p)
    aes_key = derive_key(shared_secret)
    aesgcm = AESGCM(aes_key)

    x, y = 8, 9
    plaintext = f"{x},{y}".encode()

    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    s.sendall(json.dumps({
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex()
    }).encode())

    response = json.loads(s.recv(4096).decode())
    nonce2 = bytes.fromhex(response["nonce"])
    ciphertext2 = bytes.fromhex(response["ciphertext"])

    result = aesgcm.decrypt(nonce2, ciphertext2, None)
    print("Decrypted result from server:", result.decode())
