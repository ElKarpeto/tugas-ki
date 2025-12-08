import json
import socket
import threading
import secrets
import time
from rsa import RSA

class ChatServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.nicknames = []

        # random 64-bit DES key
        self.global_des_key = secrets.token_hex(8).upper()
        print("[SERVER] DES Key:", self.global_des_key)

    def handshake(self, client, rsa: RSA):
        # generate keypair server
        e_s, d_s, n_s = rsa.generateKeys()
        public_key_server = (e_s, n_s)
        private_key_server = (d_s, n_s)

        # kirim PUBLIC KEY SERVER ke client
        payload = {
            "header": "NICK",
            "key": list(public_key_server)
        }
        client.send(json.dumps(payload).encode())

        # terima nickname & PUBLIC KEY CLIENT
        resp = client.recv(4096).decode()
        data = json.loads(resp)
        nickname = data["nickname"]
        public_key_client = tuple(data["key"])

        self.clients.append(client)
        self.nicknames.append(nickname)
        print(f"[SERVER] {nickname} connected.")

        # SIGNATURE PROPER

        # HASH DES KEY
        hashed = rsa.sha256_int(self.global_des_key)

        # SIGN hash dengan PRIVATE KEY SERVER
        signature = rsa.encrypt(hashed, private_key_server[0], private_key_server[1])

        # ENCRYPT signature pakai PUBLIC KEY CLIENT (Confidentiality)
        encrypted_signature = rsa.encrypt(
            signature,
            public_key_client[0],
            public_key_client[1]
        )

        # kirim DESKEY + SIGNATURE terenkripsi
        packet = {
            "des_key": self.global_des_key,
            "signature": str(encrypted_signature),
            "timestamp": time.time()
        }
        client.send(json.dumps(packet).encode())

        print(f"[SERVER] Sent DES key + signature to {nickname}")
