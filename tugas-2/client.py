import socket
import threading
import json
from des import DES

key = "80c4fdc3543fca7b"


class ChatClient:
    def __init__(self, host: str = 'localhost', port: int = 5555) -> None:
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.des = None
        self.nickname: str = ""

    def receive(self) -> None:
        while True:
            try:
                message = self.client.recv(4)
                if not message:
                    break

                if message == b'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                    continue

                msg_length = int.from_bytes(message, 'big')

                json_data = b''
                while len(json_data) < msg_length:
                    chunk = self.client.recv(
                        min(msg_length - len(json_data), 4096))
                    if not chunk:
                        break
                    json_data += chunk

                if not json_data:
                    break

                json_message = json.loads(json_data.decode('utf-8'))

                sender = json_message['sender']
                encrypted_text = json_message['message']
                size = json_message['size']

                try:
                    decrypted_bin = self.des.Decrypt(
                        encrypted_text, verbose=False)
                    plaintext = self.des.processOriginalText(
                        decrypted_bin, "text", size)

                    print(f"{sender}:")
                    print(f"message: {encrypted_text}")
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

                encrypted_bin = self.des.Encrypt(
                    message, 'string', verbose=False)

                full_message = {
                    'sender': self.nickname,
                    'message': encrypted_bin,
                    'size': len(message)
                }

                message_json = json.dumps(full_message)
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
