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

    def broadcast(self, message, sender_socket=None):
        # broadcast ke semua klien selain yang mengirim
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    self.remove_client(client)

    def handle_client(self, client):
        while True:
            try:
                length_data = client.recv(4)
                if not length_data:
                    self.remove_client(client)
                    break

                msg_length = int.from_bytes(length_data, 'big')

                message = b''
                while len(message) < msg_length:
                    chunk = client.recv(min(msg_length - len(message), 4096))
                    if not chunk:
                        break
                    message += chunk

                if message:
                    self.broadcast(length_data + message, client) #broadcast ke klien lain
                else:
                    self.remove_client(client)
                    break
            except Exception as e:
                print(f"Error handling client: {e}")
                self.remove_client(client)
                break

    def remove_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            self.clients.remove(client)
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)
            print(f'{nickname} DISCONNECTED')
            client.close()

    def start(self):
        rsa = RSA()

        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f'Server started on {self.host}:{self.port}')

        while True:
            client, address = self.server.accept()
            print(f'Connected with {str(address)}')

            #handshake server buat kirim header NICK
            client.send('NICK'.encode('utf-8'))
            response = client.recv(4096).decode('utf-8')
            payload = json.loads(response)

            nickname = payload.get('nickname', 'Unknown')
            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f'Nickname: {nickname}')

            # generate DES key acak for every client connect
            des_key = secrets.token_hex(8)  # 64-bit (16 hex chars)

            encrypted_key_int = rsa.encrypt(
                rsa.Hex2Int(des_key), payload['key'][0], payload['key'][1])

            # timestamp
            handshake_packet = {
                "des_key": str(encrypted_key_int),
                "timestamp": time.time()  # deteksi replay
            }

            # handshake ke klien
            client.send(json.dumps(handshake_packet).encode('utf-8'))
            print(f"Sent DES key (hex) to {nickname}: {des_key}")

            # thread penanganan pesan dari klien
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()


if __name__ == "__main__":
    host = input('Enter host (default: 0.0.0.0 for all interfaces): ') or '0.0.0.0'
    port = input('Enter port (default: 5555): ') or '5555'

    server = ChatServer(host=host, port=int(port))
    server.start()
