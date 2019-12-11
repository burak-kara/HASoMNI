import ssl
from socket import *

LINE = "\r\n"
HEADER = LINE + LINE

hostname = 'www.google.com'
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = True
context.load_default_certs()

con = socket(AF_INET, SOCK_STREAM)
con.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
con.bind(("192.168.1.34", 8080))

ssl_sock = context.wrap_socket(con, server_hostname=hostname)
ssl_sock.connect((hostname, 443))
request = "GET / HTTP/1.1" + LINE
request += "Host: " + hostname + LINE
request += "Accept: */*" + LINE
request += "User-Agent: kibitzer" + LINE
request += "Connection: Close" + HEADER
ssl_sock.sendall(request.encode('utf-8'))

response = b""
while True:
    data = ssl_sock.recv(102400)
    if not data:
        break
    response += data

ssl_sock.close()
con.close()
print(response.decode("utf-8"))
