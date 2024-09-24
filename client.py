import socket
import threading

# Client setup
nickname = input("Choose your nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 12345))

# Listening to server and sending messages
def receive():
    while True:
        try:
            # Receiving message from server
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
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
        client.send(message.encode('utf-8'))

# Starting threads for receiving and writing messages
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
