import socket
import threading
import json
import base64
import zlib
from des import DES
from rsa import RSA

class ChatClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rsa = RSA()
        self.des = None

        # generate keypair client
        e, d, n = self.rsa.generateKeys()
        self.public_key = (e, n)
        self.private_key = (d, n)

    def handshake(self):
        # 1. ambil public key server
        msg = self.client.recv(4096).decode()
        data = json.loads(msg)
        public_key_server = tuple(data["key"])

        # kirim public key + nickname
        payload = {
            "nickname": self.nickname,
            "key": list(self.public_key)
        }
        self.client.send(json.dumps(payload).encode())

        # terima DES KEY + SIGNATURE
        packet = json.loads(self.client.recv(4096).decode())

        des_key = packet["des_key"]
        encrypted_signature = int(packet["signature"])

        # buka signature → decrypt private key client
        signature = self.rsa.decrypt(
            encrypted_signature,
            self.private_key[0],
            self.private_key[1]
        )

        # verifikasi signature → decrypt pakai PUBLIC KEY SERVER
        verified_hash = self.rsa.decrypt(
            signature,
            public_key_server[0],
            public_key_server[1]
        )

        # client hitung hash sendiri
        local_hash = self.rsa.sha256_int(des_key)

        if verified_hash != local_hash:
            raise Exception("[SECURITY] Signature invalid! MITM detected!")

        print("[CLIENT] Signature verified — DES key authentic!")

        # INIT DES
        self.des = DES(des_key)
