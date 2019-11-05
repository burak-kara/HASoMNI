import socket

# create a socket object
socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 8080

# bind to the port
socket1.connect(("192.168.43.2", port))
socket2.connect_ex(("10.200.125.7", port))

# Receive no more than 1024 bytes
msg1 = socket1.recv(1024)
msg2 = socket2.recv(1024)

socket1.close()
socket2.close()

print(msg1.decode('ascii'))
print(msg2.decode('ascii'))
