import select
import socket

server_socket = socket.socket()
host = '0.0.0.0'
port = 8080
server_socket.bind((host, port))
server_socket.listen(1)
server_socket.setblocking(False)

epoll = select.epoll()
epoll.register(server_socket.fileno(), select.EPOLLIN)

connections = {}

while True:
    events = epoll.poll(-1)
    print(events)
    # break
    # 如果这里直接break，不处理事件，那么epoll.poll方法将会一直返回就绪的写事件。
    for file_no, event in events:
        if file_no == server_socket.fileno():
            print("收到socket的可读的事件（有新的连接）")
            connection, address = server_socket.accept()
            connection.setblocking(False)
            connections[connection.fileno()] = connection
            # 监听连接上的可读事件
            # epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)
            epoll.register(connection.fileno(), select.EPOLLIN)
        elif event & select.EPOLLIN:
            print("收到可读事件")
            # 监听到可读事件
            connection = connections[file_no]
            request = b""
            try:
                while True:
                    buffer = connection.recv(1)
                    if len(buffer) == 0:
                        # 客户端已关闭连接
                        print("客户端已经关闭连接")
                        break
                    request += buffer
                    break
            except socket.error as e:
                pass
            # 输出从客户端收到的请求
            print(f"request: {request}")
            # epoll.modify(connection.fileno(), select.EPOLLOUT | select.EPOLLET)
        elif event & select.EPOLLOUT:
            # 接收到可写事件
            print("收到可写事件")
            data = "这是从服务端发送的响应"
            connection = connections[file_no]
            connection.send(data.encode())
            epoll.unregister(file_no)
            connections[file_no].close()
# server_socket.close()
