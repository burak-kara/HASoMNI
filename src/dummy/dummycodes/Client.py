import socket

con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
con.bind(('192.168.1.34', 8080))
con.connect(("34.204.87.0", 8080))
con.sendall("GET /index.html HTTP/1.1\r\nHost: 34.204.87.0:8080\r\n\r\n".encode('ascii'))
response = ""
while True:
    data = con.recv(2048)
    if not data:
        break
    response += data.decode('utf-8')
print(response)
con.close()


