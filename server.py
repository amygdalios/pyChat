import socket
import threading
import sys

# Server setup
host = '127.0.0.1'  # Localhost
port = 12345        # Port to bind the server

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

# Broadcasting messages to all connected clients
def broadcast(message):
    for client in clients:
        client.send(message)

# Handling individual client connections
def handle_client(client):
    while True:
        try:
            # Receiving messages from clients
            message = client.recv(1024)
            broadcast(message)
        except:
            # Removing clients on disconnect
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat.'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Graceful shutdown to notify clients
def shutdown_server():
    broadcast("SERVER_SHUTDOWN".encode('utf-8'))
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

            # Requesting nickname from the client
            client.send("NICK".encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            nicknames.append(nickname)
            clients.append(client)

            print(f"Nickname of the client is {nickname}")
            broadcast(f"{nickname} joined the chat!".encode('utf-8'))
            client.send('Connected to the server!'.encode('utf-8'))

            # Handling individual client in a new thread
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start()

        except KeyboardInterrupt:
            print("\nShutting down the server...")
            shutdown_server()

print("Server is listening...")
receive()
