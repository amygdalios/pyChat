import socket
import threading
from cryptography.fernet import Fernet

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
print(f"Received encryption key: {key.decode('utf-8')}")  # Print the received key
cipher = Fernet(key)  # Create a Fernet cipher

# Listening to server and sending messages
def receive():
    while True:
        try:
            # Receiving encrypted message from server
            encrypted_message = client.recv(1024)
            message = cipher.decrypt(encrypted_message).decode('utf-8')
            if message == 'NICK':
                client.send(cipher.encrypt(nickname.encode('utf-8')))
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

def write():
    while True:
        message = f'{nickname}: {input("")}'
        encrypted_message = cipher.encrypt(message.encode('utf-8'))
        client.send(encrypted_message)

# Starting threads for receiving and writing messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
