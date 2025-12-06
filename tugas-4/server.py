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

        # Generate DES key GLOBAL sekali aja pak
        self.global_des_key = "1234567890ABCDEF"  # 64-bit DES key (16 hex)
        print(f"[SERVER] Global DES key: {self.global_des_key}")

    def broadcast(self, message, sender_socket=None):
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
                    self.broadcast(length_data + message, client)
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
            nickname = self.nicknames[index]
            print(f"{nickname} DISCONNECTED")

            self.clients.remove(client)
            self.nicknames.remove(nickname)
            client.close()

    def handshake(self, client, rsa: RSA):
        e, d, n = rsa.generateKeys()
        public_key = (e, n)
        private_key = (d, n)

        # kriim public key server ke client
        payload = {
            "header": "NICK",
            "key": list(public_key),
        }
        client.send(json.dumps(payload).encode('utf-8'))

        # simpan public key client
        response = client.recv(4096).decode('utf-8')
        payload = json.loads(response)
        nickname = payload.get('nickname', 'Unknown')
        public_key_client = tuple(payload['key'])

        self.nicknames.append(nickname)
        self.clients.append(client)

        print(f"Nickname: {nickname}")

        # encryt DES key dengan private key server -> public key client
        encrypted_key1 = rsa.encrypt(
            rsa.Hex2Int(self.global_des_key), private_key[0], private_key[1]
        )

        encrypted_key2 = rsa.encrypt(
            encrypted_key1, public_key_client[0], public_key_client[1]
        )

        # kirim DES key
        handshake_packet = {
            "key": str(encrypted_key2),
            "timestamp": time.time()
        }

        client.send(json.dumps(handshake_packet).encode('utf-8'))
        print(f"[SERVER] Sent DES key to {nickname}")

    def start(self):
        rsa = RSA()

        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"[SERVER] Running on {self.host}:{self.port}")

        while True:
            client, address = self.server.accept()
            print(f"Connected with {address}")

            self.handshake(client, rsa)

            thread = threading.Thread(
                target=self.handle_client, args=(client,))
            thread.start()


if __name__ == "__main__":
    host = input("Host (default 0.0.0.0): ") or "0.0.0.0"
    port = input("Port (default 5555): ") or "5555"

    server = ChatServer(host, int(port))
    server.start()
