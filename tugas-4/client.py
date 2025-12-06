import socket
import threading
import json
import base64
import zlib
import time
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

        # RSA keypair
        e, d, n = self.rsa.generateKeys()
        self.public_key = (e, n)
        self.private_key = (d, n)

    def b64e(self, b: bytes) -> str:
        return base64.b64encode(b).decode("ascii")

    def b64d(self, s: str) -> bytes:
        return base64.b64decode(s.encode("ascii"))

    def bitstr_to_bytes(self, bits: str) -> bytes:
        if len(bits) % 8 != 0:
            bits += "0" * (8 - (len(bits) % 8))
        return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

    def bytes_to_bitstr(self, b: bytes) -> str:
        return "".join(f"{byte:08b}" for byte in b)

    # HANDSHAKE: terima DES key GLOBAL yang wis dibikin
    def handshake(self):
        # ambil public key server
        message = self.client.recv(4096).decode('utf-8')
        payload = json.loads(message)

        header = payload.get('header', '')
        if header != "NICK":
            raise Exception("Invalid handshake header")

        public_key_server = tuple(payload['key'])

        # kirim public key client
        payload = {
            'nickname': self.nickname,
            'key': list(self.public_key)
        }
        self.client.send(json.dumps(payload).encode('utf-8'))

        # ambil encrypted DES key
        encrypted_key = self.client.recv(4096).decode('utf-8')
        packet = json.loads(encrypted_key)

        encripted_des_key = int(packet["key"])

        # decrypt DES key, private key client -> public key server
        des_key1 = self.rsa.decrypt(
            encripted_des_key, self.private_key[0], self.private_key[1])

        des_key2 = self.rsa.decrypt(
            des_key1, public_key_server[0], public_key_server[1])

        des_key = self.rsa.Int2hex(des_key2)

        print(f"[CLIENT] Received DES key: {des_key}")
        self.des = DES(des_key)

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

                msg = json.loads(data.decode('utf-8'))

                sender = msg["sender"]
                enc_b64 = msg["message"]
                size = msg["size"]
                seq = msg["seq"]
                recv_crc = msg["crc32"]

                ct_bytes = self.b64d(enc_b64)
                calc_crc = zlib.crc32(ct_bytes) & 0xffffffff
                if calc_crc != recv_crc:
                    print("[DROP] CRC mismatch")
                    continue

                ct_bits = self.bytes_to_bitstr(ct_bytes)

                decrypted = self.des.Decrypt(ct_bits, verbose=False)
                plaintext = self.des.processOriginalText(
                    decrypted, "text", size)

                print(f"[seq {seq}] {sender}: {plaintext}")

            except:
                print("[ERROR] Lost connection.")
                self.client.close()
                break

    # SEND
    def send(self):
        while True:
            try:
                text = input('')
                if text.lower() == '/quit':
                    self.client.close()
                    break

                enc_bits = self.des.Encrypt(text, 'string', verbose=False)
                ct_bytes = self.bitstr_to_bytes(enc_bits)
                enc_b64 = self.b64e(ct_bytes)

                self.seq_send += 1
                crc = zlib.crc32(ct_bytes) & 0xffffffff

                msg = {
                    'sender': self.nickname,
                    'message': enc_b64,
                    'size': len(text),
                    'seq': self.seq_send,
                    'crc32': crc
                }

                raw = json.dumps(msg).encode('utf-8')
                header = len(raw).to_bytes(4, 'big')
                self.client.send(header + raw)

            except Exception as e:
                print("Send error:", e)
                self.client.close()
                break

    # START
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
