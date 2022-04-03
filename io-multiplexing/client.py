import socket
import time

client_socket = socket.socket()
host = "0.0.0.0"
port = 8080
client_socket.connect((host, port))
client_socket.send(b"hello")
# for c in "abc":
#     data = c * 3
#     client_socket.send(data.encode())

# data = client_socket.recv(1024)
# print(data.decode())
client_socket.close()
