import socket
import threading
import json
import base64
import zlib
from des import DES

key = "80c4fdc3543fca7b"


def b64e(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")


def b64d(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))


def bitstr_to_bytes(bits: str) -> bytes:
    # prepare lek  bukan kelipatan 8
    if len(bits) % 8 != 0:
        bits = bits + "0" * (8 - (len(bits) % 8))
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


def bytes_to_bitstr(b: bytes) -> str:
    return "".join(f"{byte:08b}" for byte in b)


class ChatClient:
    def __init__(self, host: str = 'localhost', port: int = 5555) -> None:
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.des = None
        self.nickname: str = ""
        # sequence number sederhana untuk pengiriman
        self.seq_send: int = 0  

    def receive(self) -> None:
        while True:
            try:
                # baca header 4 byte (panjang payload) ATAU "NICK"
                header = self.client.recv(4)
                if not header:
                    break

                # handshake nickname
                if header == b'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                    continue

                msg_length = int.from_bytes(header, 'big')

                # baca payload JSON sesuai panjang
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

                # ---- upgrade: verifikasi CRC32 di atas bytes ciphertext
                ct_bytes = b64d(enc_b64)
                calc_crc = zlib.crc32(ct_bytes) & 0xffffffff
                if recv_crc is None or int(recv_crc) != calc_crc:
                    print(f"\n[DROP] CRC mismatch (pesan diduga diubah). from={sender} seq={seq}")
                    continue

                # konversi lagi ke bitstring biar kompatibel ama DES.Decrypt()
                ct_bits = bytes_to_bitstr(ct_bytes)

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
                    print(f"\n[Error decrypting message from {sender}: {e}]")
            except Exception as e:
                print(f'\n[Connection error: {e}]')
                self.client.close()
                break

    def send(self) -> None:
        while True:
            try:
                message = str(input(''))
                if message.lower() == '/quit':
                    self.client.close()
                    break

                # enkripsi -> dapat bitstring dari DES.Encrypt
                encrypted_bits = self.des.Encrypt(message, 'string', verbose=False)

                # kirim sebagai base64, plus CRC32 dan seq
                ct_bytes = bitstr_to_bytes(encrypted_bits)
                enc_b64 = b64e(ct_bytes)

                self.seq_send += 1
                crc = zlib.crc32(ct_bytes) & 0xffffffff

                full_message = {
                    'sender': self.nickname,
                    'message': enc_b64,     # base64
                    'size': len(message),   # trim plaintext
                    'seq': self.seq_send,   # nomor urut so log jadi rapi
                    'crc32': crc            # checksum ringan untuk demo tamper detect
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
        self.des = DES(key)

        try:
            self.client.connect((self.host, self.port))
            print(f'Connected to server at {self.host}:{self.port}')
            print('Type /quit to exit\n')

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
