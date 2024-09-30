import socket
import threading
from cryptography.fernet import Fernet

from infrastructure.messaging import MessageService

def main():
    # Client setup
    nickname = input("Choose your nickname: ")

    # Asking for the IP and port of the server
    server_info = input("Enter server IP and port (format: IP:PORT): ")
    server_ip, server_port = server_info.split(":")
    server_port = int(server_port)  # Convert the port to an integer

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))

    # Receive the encryption key from the server
    key = client.recv(1024)  # Receive the key
    cipher = Fernet(key)  # Create a Fernet cipher

    messager = MessageService(cipher)

    # Starting threads for receiving and writing messages
    receive_thread = threading.Thread(target=receive, args=(nickname, messager, client))
    write_thread = threading.Thread(target=write, args=(nickname, messager, client))

    receive_thread.start()
    write_thread.start()


# Listening to server and sending messages
def receive(nickname: str, messager: MessageService, client: socket):
    while True:
        try:
            # Receiving encrypted message from server
            encrypted_message = client.recv(1024)
            message = messager.decrypt(encrypted_message)
            if message == 'NICK':
                client.send(messager.encrypt(nickname))
            elif message == 'SERVER_SHUTDOWN':
                print("Server is shutting down... Disconnecting.")
                client.close()
                break
            else:
                print(message)
        except:
            # If error or server shutdown, close connection
            print("An error occurred or the server has closed!")
            client.close()
            break

def write(nickname: str, messager: MessageService, client: socket):
    while True:
        message = f'{nickname}: {input("")}'
        encrypted_message = messager.encrypt(message)
        client.send(encrypted_message)

if __name__ == '__main__':
    main()