import socket

con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
con.bind(("10.200.106.78", 8080))
con.connect(("34.204.87.0", 8080))
con.sendall("HEAD / HTTP/1.1\r\n\r\n".encode('ascii'))
response = con.recv(2048).decode("utf-8").split("\r\n")
d = {}
for line in response:
    print(line)
    if line.__contains__(":"):
        key = line.split(":")[0]
        value = line.split(":")[1][1:]
        d[key] = value

print(d)
con.close()
