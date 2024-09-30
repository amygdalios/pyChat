import socket
import threading
import sys
import os
from cryptography.fernet import Fernet

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

def encrypt(cipher: Fernet, message: str) -> bytes:
    return cipher.encrypt(message.encode('utf-8'))

def decode(cipher: Fernet, message: bytes) -> str:
    return cipher.decrypt(message).decode('utf-8')

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
            message = cipher.decrypt(encrypted_message).decode('utf-8')
            broadcast(cipher.encrypt(message.encode('utf-8')))
        except:
            # Removing clients on disconnect
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(cipher.encrypt(f'{nickname} left the chat.'.encode('utf-8')))
            nicknames.remove(nickname)
            break

# Graceful shutdown to notify clients
def shutdown_server():
    broadcast(cipher.encrypt("SERVER_SHUTDOWN".encode('utf-8')))
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
            client.send(cipher.encrypt("NICK".encode('utf-8')))
            nickname = cipher.decrypt(client.recv(1024)).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)

            print(f"Nickname of the client is {nickname}")
            broadcast(cipher.encrypt(f"{nickname} joined the chat!".encode('utf-8')))
            client.send(cipher.encrypt('Connected to the server!'.encode('utf-8')))

            # Handling individual client in a new thread
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()

        except KeyboardInterrupt:
            print("\nShutting down the server...")
            shutdown_server()

print("Server online")
receive()