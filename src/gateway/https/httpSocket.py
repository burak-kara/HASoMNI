from socket import *
import ssl
import requests as req
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

MOBILE_IP = '192.168.1.34'
MOBILE_PORT = 8080

REQUESTED = ''

REQUESTED_HOSTNAME = "techslides.com"
REQUESTED_PATH = "demos/sample-videos/small.mp4"
LINE = "\r\n"
HEADER = LINE + LINE

con = socket(AF_INET, SOCK_STREAM)
con.bind((MOBILE_IP, MOBILE_PORT))
con.connect((REQUESTED_HOSTNAME, 80))
request = "HEAD /" + REQUESTED_PATH + " HTTP/1.1" + LINE
# # request += "User-Agent: PostmanRuntime/7.20.1" + LINE
# request += "Accept: */*" + LINE
# request += "Cache-Control: no-cache" + LINE
request += "Host: " + REQUESTED_HOSTNAME + LINE
# request += "Accept-Encoding: gzip, deflate" + LINE
request += "Connection: Close" + HEADER
print(request)
con.sendall(request.encode("ascii"))
# con.recv(2048)
response = b""
while True:
    data = con.recv(2048)
    print(data.decode("utf-8"))
    if not data:
        break
    response += data
print("--")
print(response.decode("utf-8"))
con.close()
