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

    def broadcast(self, message, sender_socket=None):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            nickname = self.nicknames[index]
            print(f"{nickname} DISCONNECTED")

            self.clients.remove(client)
            self.nicknames.remove(nickname)
            client.close()

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
                print(f"Error: {e}")
                self.remove_client(client)
                break

    def handshake(self, client, rsa: RSA):
        # 1. Setup Key Server
        e_s, d_s, n_s = rsa.generateKeys()
        public_key_server = (e_s, n_s)
        private_key_server = (d_s, n_s)

        # 2. Tukar Public Key
        # Kirim Public Key Server
        payload = {
            "header": "NICK",
            "key": list(public_key_server)
        }
        client.send(json.dumps(payload).encode())

        # Terima Public Key Client
        resp = client.recv(4096).decode()
        data = json.loads(resp)
        nickname = data["nickname"]
        public_key_client = tuple(data["key"])

        self.clients.append(client)
        self.nicknames.append(nickname)
        print(f"[SERVER] {nickname} connected.")

        signature = rsa.encrypt(rsa.Hex2Int(
            self.global_des_key), private_key_server[0], private_key_server[1])
        encrypted_des_key = rsa.encrypt(rsa.Hex2Int(
            self.global_des_key), public_key_client[0], public_key_client[1])

        message_packet = {
            "enc_des_key": encrypted_des_key,
            "signature": signature
        }

        client.send(json.dumps(message_packet).encode())

        print(f"[SERVER] Sent Encrypted DES key + Signature to {nickname}")

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
