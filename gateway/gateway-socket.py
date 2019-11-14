import socket

SERVER_ADDRESS = '172.31.84.69'
INTERFACE_ADDRESS = "192.168.0.41"
PORT = 8080

requester_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
requester_socket.bind((INTERFACE_ADDRESS, 0))
requester_socket.connect((SERVER_ADDRESS, PORT))

#request = b"GET / HTTP/1.1\r\nHOST: \r\nUser-Agent: Custom/0.0.1\r\nAccept: */*\r\n\n"


requester_socket.sendall(b"HEAD /172.31.84.69 HTTP/1.1\r\nAccept: text/html\r\n\r\n")
print(str(requester_socket.recv(1024), 'utf-8'))
#requester_socket.send(request)
#result = requester_socket.recv(1024)

# while len(result) > 0:
#    print(result)
#   result = requester_socket.recv(1024)

requester_socket.close()
