import socket
import threading
import sys
from cryptography.fernet import Fernet

from infrastructure.messaging import MessageService

# Server setup
host = '127.0.0.1'  # Localhost
port = 5555        # Port to bind the server

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []
key = Fernet.generate_key()  # Generate a key
cipher = Fernet(key)  # Create a Fernet cipher

message_service = MessageService(cipher)

# Broadcasting messages to all connected clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Handling individual client connections
def handle_client(client):
    while True:
        try:
            # Receiving messages from clients
            encrypted_message = client.recv(1024)
            message = message_service.decrypt(encrypted_message)

            print(f'Received: {message}')

            broadcast(message_service.encrypt(message))
        except:
            # Removing clients on disconnect
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]

            disconnect_message = message_service.encrypt(f'{nickname} left the chat.')
            broadcast(disconnect_message)
            nicknames.remove(nickname)
            break

# Graceful shutdown to notify clients
def shutdown_server():
    shutdown_message = message_service.encrypt('SERVER_SHUTDOWN')
    broadcast(shutdown_message)
    for client in clients:
        client.close()
    server.close()
    sys.exit(0)

# Receiving / accepting clients
def receive():
    while True:
        try:
            client, address = server.accept()
            print(f"Connected with {str(address)}")

            # Sending the encryption key to the client
            client.send(key)

            # Requesting nickname from the client
            client.send(message_service.encrypt('NICK'))
            nickname = message_service.decrypt(client.recv(1024))

            nicknames.append(nickname)
            clients.append(client)

            print(f'Nickname of the client is {nickname}')
            broadcast(message_service.encrypt(f'{nickname} joined the chat!'))
            client.send(message_service.encrypt('Connected to the server!'))

            # Handling individual client in a new thread
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()

            print(f'Started thread with ID {thread.ident}')

        except KeyboardInterrupt:
            print("\nShutting down the server...")
            shutdown_server()

print("Server online")
receive()