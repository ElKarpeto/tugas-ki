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
        self.nickname = ""
        self.seq_send = 0

        # generate RSA keypair for the client
        e, d, n = self.rsa.generateKeys()
        self.public_key = (e, n)
        self.private_key = (d, n)

    # Base64 helpers
    def b64e(self, b: bytes) -> str:
        return base64.b64encode(b).decode("ascii")

    def b64d(self, s: str) -> bytes:
        return base64.b64decode(s.encode("ascii"))

    # bit helpers
    def bitstr_to_bytes(self, bits: str) -> bytes:
        if len(bits) % 8 != 0:
            bits += "0" * (8 - (len(bits) % 8))
        return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

    def bytes_to_bitstr(self, b: bytes) -> str:
        return "".join(f"{byte:08b}" for byte in b)

    # ================================
    # HANDSHAKE (Signature Verify)
    # ================================
    def handshake(self):
        # 1. receive public key server
        message = self.client.recv(4096).decode()
        payload = json.loads(message)

        if payload.get("header") != "NICK":
            raise Exception("Invalid handshake header")

        public_key_server = tuple(payload["key"])

        # 2. send nickname + public key client
        payload = {
            "nickname": self.nickname,
            "key": list(self.public_key)
        }
        self.client.send(json.dumps(payload).encode())

        # 3. receive DES key + encrypted signature
        packet = json.loads(self.client.recv(4096).decode())

        des_key = packet["des_key"]
        encrypted_signature = int(packet["signature"])

        # 4. decrypt signature with client private key
        signature = self.rsa.decrypt(
            encrypted_signature,
            self.private_key[0],
            self.private_key[1]
        )

        # 5. verify signature using server PUBLIC KEY
        verified_hash = self.rsa.decrypt(
            signature,
            public_key_server[0],
            public_key_server[1]
        )

        # 6. compute local hash
        local_hash = self.rsa.sha256_int(des_key)

        if verified_hash != local_hash:
            raise Exception("[SECURITY] Invalid Signature! DES key is not authentic.")
        
        print("[CLIENT] Signature verified — DES key authentic!")
        print(f"[CLIENT] DES key: {des_key}")

        # Initialize DES
        self.des = DES(des_key)

    # ================================
    # RECEIVE
    # ================================
    def receive(self):
        while True:
            try:
                header = self.client.recv(4)
                if not header:
                    break

                msg_length = int.from_bytes(header, 'big')
                data = b''

                while len(data) < msg_length:
                    chunk = self.client.recv(min(4096, msg_length - len(data)))
                    if not chunk:
                        break
                    data += chunk

                msg = json.loads(data.decode())

                sender = msg["sender"]
                enc_b64 = msg["message"]
                size = msg["size"]
                seq = msg["seq"]
                recv_crc = msg["crc32"]

                ct_bytes = self.b64d(enc_b64)

                # CRC check
                calc_crc = zlib.crc32(ct_bytes) & 0xffffffff
                if calc_crc != recv_crc:
                    print("[DROP] CRC mismatch")
                    continue

                ct_bits = self.bytes_to_bitstr(ct_bytes)

                decrypted = self.des.Decrypt(ct_bits, verbose=False)
                plaintext = self.des.processOriginalText(decrypted, "text", size)

                print(f"[seq {seq}] {sender}: {plaintext}")

            except Exception as e:
                print("Receive error:", e)
                self.client.close()
                break

    # ================================
    # SEND
    # ================================
    def send(self):
        while True:
            try:
                text = input("")
                if text.lower() == "/quit":
                    self.client.close()
                    break

                enc_bits = self.des.Encrypt(text, "string", verbose=False)
                ct_bytes = self.bitstr_to_bytes(enc_bits)
                enc_b64 = self.b64e(ct_bytes)

                self.seq_send += 1
                crc = zlib.crc32(ct_bytes) & 0xffffffff

                msg = {
                    "sender": self.nickname,
                    "message": enc_b64,
                    "size": len(text),
                    "seq": self.seq_send,
                    "crc32": crc
                }

                raw = json.dumps(msg).encode()
                header = len(raw).to_bytes(4, "big")
                self.client.send(header + raw)

            except Exception as e:
                print("Send error:", e)
                self.client.close()
                break

    # ================================
    # START
    # ================================
    def start(self):
        self.nickname = input("Enter nickname: ")

        try:
            self.client.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")

            self.handshake()

            threading.Thread(target=self.receive, daemon=True).start()
            self.send()

        except Exception as e:
            print("Connection failed:", e)


if __name__ == "__main__":
    host = input("Server host (default localhost): ") or "localhost"
    port = input("Server port (default 5555): ") or "5555"

    ChatClient(host, int(port)).start()
