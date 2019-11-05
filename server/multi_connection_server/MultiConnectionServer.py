import socket

import socket

# create a socket object
socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 8080

# bind to the port
socket1.bind(("192.168.1.34", port))
socket2.bind(("192.168.43.17", port))

# queue up to 5 requests
socket1.listen(5)
socket2.listen(5)

while True:
    # establish a connection
    clientSocket1, addr1 = socket1.accept()
    clientSocket2, addr2 = socket2.accept()

    print("Got a connection from %s" % str(addr1))
    print("Got a connection from %s" % str(addr2))

    msg1 = 'Thank you for connecting 1' + "\r\n"
    msg2 = 'Thank you for connecting 2' + "\r\n"
    clientSocket1.send(msg1.encode('ascii'))
    clientSocket2.send(msg2.encode('ascii'))
    clientSocket1.close()
    clientSocket2.close()
