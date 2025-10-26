import socket
import threading


class ChatServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.nicknames = []

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
            self.clients.remove(client)
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)
            print(f'{nickname} DISCONNECTED')
            client.close()

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f'Server started on {self.host}:{self.port}')

        while True:
            client, address = self.server.accept()
            print(f'Connected with {str(address)}')

            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')

            self.nicknames.append(nickname)
            self.clients.append(client)

            print(f'Nickname: {nickname}')

            thread = threading.Thread(
                target=self.handle_client, args=(client,))
            thread.start()


if __name__ == "__main__":
    print('=== DES Encrypted Chat Server ===\n')
    host = input(
        'Enter host (default: 0.0.0.0 for all interfaces): ') or '0.0.0.0'
    port = input('Enter port (default: 5555): ') or '5555'

    server = ChatServer(host=host, port=int(port))
    server.start()
