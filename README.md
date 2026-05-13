# Diffie–Hellman Key Exchange with AES-GCM Encryption

A Python demonstration of secure key exchange, authenticated encryption, and Man-in-the-Middle attack simulation over TCP sockets — built for learning cryptography and network security fundamentals.

---

## Overview

This project walks through a complete secure communication pipeline:

1. **Key Exchange** — Client and server derive a shared secret via Diffie–Hellman without ever transmitting it directly
2. **Encryption** — Messages are encrypted with AES-GCM, authenticated to prevent tampering
3. **MITM Simulation** — An intruder relays traffic transparently, demonstrating what an attacker sees (and cannot see)

---

## Project Structure

```
DHM/
├── client.py       # Initiates key exchange and sends encrypted messages
├── server.py       # Receives, decrypts, and processes client data
├── intruder.py     # Transparent MITM relay for traffic interception
└── README.md
```

---

## How It Works

### 1. Diffie–Hellman Key Exchange

The client generates a large prime `p`, a generator `g`, and a private key `a`. The server generates its own private key `b`. Each party sends their public value over the network:

```
Client sends:  A = g^a mod p
Server sends:  B = g^b mod p
```

Both sides independently compute the same shared secret:

```
shared_secret = B^a mod p  (client)
              = A^b mod p  (server)
```

The secret is never transmitted — only the public halves are.

### 2. AES-GCM Encryption

The shared secret is hashed with SHA-256 to produce a 256-bit AES key. All subsequent messages are encrypted using AES-GCM, which provides both confidentiality and authenticity. A unique nonce is generated per message.

### 3. MITM Simulation

`intruder.py` sits between client and server, forwarding all traffic:

```
Client ──► Intruder ──► Server
Client ◄── Intruder ◄── Server
```

The intruder can read the plaintext key exchange parameters (`p`, `g`, `A`, `B`) but cannot decrypt the AES-GCM ciphertext without the shared secret — demonstrating why authenticated encryption matters even when the channel is compromised.

---

## Requirements

```bash
pip install cryptography
```

Python 3.7+ is required. No other dependencies.

---

## Running the Project

Start each component in a separate terminal, in this order:

```bash
# 1. Start the server
python server.py

# 2. Start the MITM intruder
python intruder.py

# 3. Run the client
python client.py
```

> To run without the intruder, point the client directly at the server's port.

---

## Example Output

**Client**
```
C:\Users\Desktop\DHM>python client.py
Enter a prime number p: 23
Prime p verified: 23
Generator g found: 5
Decrypted result from server: 72
```

**Server**
```
C:\Users\Desktop\DHM>python server.py
Server listening...
Connected by ('127.0.0.1', 51500)
Server decrypted numbers: 8, 9
```

**Intruder**
```
C:\Users\Desktop\DHM>python intruder.py
[INTRUDER] Listening for client...
[INTRUDER] Client connected
[INTRUDER] Connected to real server
[INTRUDER] Intercepted Client → Server:
{"p": 23, "g": 5, "A": 19}

[INTRUDER] Intercepted Server → Client:
{"B": 8}

[INTRUDER] Intercepted Client → Server:
{"nonce": "5fe29ad56caf94305b7f08bf", "ciphertext": "0bfb000d966077407f071d61ae2c76ce3d0df7"}

[INTRUDER] Intercepted Server → Client:
{"nonce": "58e2e53039a492f7dc4c7d6a", "ciphertext": "0a5c8065565acff04b4d4141d57765651ae1"}

[INTRUDER] Connection aborted in Client → Server
```

The intruder sees the full DH handshake in plaintext (`p`, `g`, `A`, `B`) but receives only opaque nonce/ciphertext pairs for all encrypted messages — with no way to decrypt them without the shared secret.

---

## Concepts Covered

| Concept | Where |
|---|---|
| Diffie–Hellman Key Exchange | `client.py`, `server.py` |
| AES-GCM Authenticated Encryption | `client.py`, `server.py` |
| SHA-256 Key Derivation | `client.py`, `server.py` |
| TCP Socket Programming | All files |
| Man-in-the-Middle Attack | `intruder.py` |

---

## Security Notes

- The small prime (`p = 23`) used in the example output is for readability only. A real implementation requires a cryptographically large prime (2048-bit minimum).
- This project does **not** include public key authentication, so the DH exchange itself is vulnerable to an active MITM who replaces public values — a gap intentionally left open for discussion.
- AES-GCM nonces must never be reused under the same key. Ensure proper nonce management in any production-derived code.

---

## Disclaimer

This project is strictly for educational use. It is intended to illustrate cryptographic and networking concepts in a controlled, local environment.

---

## Author

**Daniel Nicolas Rentapalli** — Cryptography & Network Security Demonstration
MSc Cyber Security Student  
Swansea University  
This project was developed as part of the **2526_CSCM888 / CSMM88 – Network, Wireless & Cloud Security** module at Swansea University.
