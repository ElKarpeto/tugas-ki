import socket
import threading
import json
import base64
import zlib
import time
from des import DES
from rsa import RSA


class ChatClient:
    def __init__(self, host: str = 'localhost', port: int = 5555) -> None:
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.des = None
        self.rsa = RSA()
        self.nickname: str = ""
        self.seq_send: int = 0

        # generate RSA key
        e, d, n = self.rsa.generateKeys()
        self.public_key = (e, n)
        self.private_key = (d, n)

    def b64e(self, b: bytes) -> str:
        return base64.b64encode(b).decode("ascii")

    def b64d(self, s: str) -> bytes:
        return base64.b64decode(s.encode("ascii"))

    def bitstr_to_bytes(self, bits: str) -> bytes:
        if len(bits) % 8 != 0:
            bits = bits + "0" * (8 - (len(bits) % 8))
        return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))

    def bytes_to_bitstr(self, b: bytes) -> str:
        return "".join(f"{byte:08b}" for byte in b)

    def handshake(self):
        # handshake dari server "NICK"
        header = self.client.recv(4)
        if header != b"NICK":
            raise Exception("Expected NICK header from server")

        # kirim nickname ama public key
        payload = {
            'nickname': self.nickname,
            'key': list(self.public_key)
        }
        self.client.send(json.dumps(payload).encode('utf-8'))

        # nerima handshake packet dari JSON
        encrypted_key_json = self.client.recv(4096).decode('utf-8')
        packet = json.loads(encrypted_key_json)

        # retrieve key yang udah keenkripsi plus ama timestampnya
        encrypted_key_int = int(packet["des_key"])
        timestamp = packet.get("timestamp", 0)

        d, n = self.private_key
        des_key_int = self.rsa.decrypt(encrypted_key_int, d, n)
        des_key = self.rsa.Int2hex(des_key_int)

        # validasi timestamp tok
        if abs(time.time() - timestamp) > 120:  # 2 menit max, ojok kelamaan wkkwwk
            raise Exception("Handshake expired or replay detected")

        print(f"Received DES key (hex): {des_key}")
        self.des = DES(des_key)

    def receive(self) -> None:
        while True:
            try:
                header = self.client.recv(4)
                if not header:
                    break

                msg_length = int.from_bytes(header, 'big')

                json_data = b''
                while len(json_data) < msg_length:
                    chunk = self.client.recv(min(msg_length - len(json_data), 4096))
                    if not chunk:
                        break
                    json_data += chunk

                if not json_data:
                    break

                obj = json.loads(json_data.decode('utf-8'))

                sender = obj.get('sender', 'UNKNOWN')
                enc_b64 = obj.get('message', '')
                size = int(obj.get('size', 0))
                seq = obj.get('seq', None)
                recv_crc = obj.get('crc32', None)

                ct_bytes = self.b64d(enc_b64)
                calc_crc = zlib.crc32(ct_bytes) & 0xffffffff
                if recv_crc is None or int(recv_crc) != calc_crc:
                    print(f"\n[DROP] CRC mismatch. From={sender} seq={seq}")
                    continue

                ct_bits = self.bytes_to_bitstr(ct_bytes)

                try:
                    decrypted_bits = self.des.Decrypt(ct_bits, verbose=False)
                    plaintext = self.des.processOriginalText(decrypted_bits, "text", size)

                    if seq is not None:
                        print(f"[seq {seq}] {sender}:")
                    else:
                        print(f"{sender}:")
                    print(f"cipher (base64): {enc_b64}")
                    print(f"plaintext: {plaintext}\n")
                except Exception as e:
                    print(f"[Error decrypting message from {sender}: {e}]")
            except Exception as e:
                print(f'\n[Connection error: {e}]')
                self.client.close()
                break

    def send(self) -> None:
        while True:
            try:
                message = str(input(''))
                if message == '':
                    continue

                if message.lower() == '/quit':
                    self.client.close()
                    break

                encrypted_bits = self.des.Encrypt(message, 'string', verbose=False)

                ct_bytes = self.bitstr_to_bytes(encrypted_bits)
                enc_b64 = self.b64e(ct_bytes)

                self.seq_send += 1
                crc = zlib.crc32(ct_bytes) & 0xffffffff

                full_message = {
                    'sender': self.nickname,
                    'message': enc_b64,
                    'size': len(message),
                    'seq': self.seq_send,
                    'crc32': crc
                }

                message_json = json.dumps(full_message, ensure_ascii=False)
                message_bytes = message_json.encode('utf-8')

                length_header = len(message_bytes).to_bytes(4, 'big')
                self.client.send(length_header + message_bytes)
            except Exception as e:
                print(f"\n[Send error: {e}]")
                self.client.close()
                break

    def start(self):
        self.nickname = input('Enter your nickname: ')

        try:
            self.client.connect((self.host, self.port))
            print(f'Connected to server at {self.host}:{self.port}')
            print('Type /quit to exit\n')

            self.handshake()

            receive_thread = threading.Thread(target=self.receive)
            receive_thread.daemon = True
            receive_thread.start()

            self.send()
        except Exception as e:
            print(f'Could not connect to server: {e}')


if __name__ == "__main__":
    host = input('Enter server host: ') or 'localhost'
    port = input('Enter server port (e.g. 5555): ') or '5555'

    client = ChatClient(host, int(port))
    client.start()
