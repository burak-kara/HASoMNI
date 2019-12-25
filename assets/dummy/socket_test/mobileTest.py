from socket import *
import time

WIFI_IP = '192.168.1.34'
MOBILE_IP = '192.168.43.38'
LAN_IP = '192.168.1.38'
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
PORT = 8080

REQUESTED_IP = "34.204.87.0"
REQUESTED_PORT = 8080
REQUESTED_FILE = "index.html"

LINE = "\r\n"
HEADER = LINE + LINE
MOBILE_RANGE_START = 0

con = socket(AF_INET, SOCK_STREAM)
con.bind((WIFI_IP, PORT))
con.connect((REQUESTED_IP, int(REQUESTED_PORT)))
request = "GET /" + REQUESTED_FILE + " HTTP/1.1" + LINE
request += "Connection: keep-alive" + LINE
request += "Range: bytes=" + str(MOBILE_RANGE_START) + "-371" + HEADER
con.sendall(request.encode("ascii"))
response = b""
while True:
    data = con.recv(2048)
    if not data:
        break
    response += data
print(response.split(HEADER.encode("utf-8"), 1)[1])
# con.shutdown(SHUT_RDWR)
con.close()
print("-----------------------------------------------")

# time.sleep(1)
con = socket(AF_INET, SOCK_STREAM)
# con.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
con.bind((WIFI_IP, PORT+1))
con.connect((REQUESTED_IP, int(REQUESTED_PORT)))
request = "GET /" + REQUESTED_FILE + " HTTP/1.1" + LINE
request += "Connection: close" + LINE
request += "Range: bytes=" + str(MOBILE_RANGE_START) + "-371" + HEADER
con.sendall(request.encode("ascii"))
response = b""
while True:
    data = con.recv(2048)
    if not data:
        break
    response += data
print(response.split(HEADER.encode("utf-8"), 1)[1])
con.close()
