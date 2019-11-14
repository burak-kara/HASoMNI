import http.client as hc
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, SimpleHTTPRequestHandler

WIFI_IP = '10.200.106.78'
MOBILE_IP = '192.168.43.17'
LAN_IP = '192.168.1.38'
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
PORT = 8080
REQUESTED_IP = ''
REQUESTED_PORT = 0
REQUESTED_FILE = ''


# Required for clean coding
# def do_Connection(requested, connection_load):
#     connection = hc.HTTPConnection(requested[0], requested[1])
#     headers = {'Connection': 'Keep-Alive', 'Range': connection_load}
#     connection.request("GET", "/" + requested[2], body=None, headers=headers)
#     response = connection.getresponse()
#     connection.close()
#     try:
#         response = response.read()
#     except hc.IncompleteRead as e:
#         response = e.partial
#     return response
#
#
# def do_Thread_Connection(requested, connection_load):
#     lan = ThreadingHTTPServer((LAN_ADDRESS, 8081), Proxy)
#     lan.serve_forever()
#     response = do_Connection(requested, connection_load)
#     lan.shutdown()
#     return response

def tryTwoConnection():
    print(REQUESTED_PORT)
    # path1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    path2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    connection1 = hc.HTTPConnection(REQUESTED_IP, int(REQUESTED_PORT))

    connection1.request("GET", "/")
    connection1.close()

    # might be handy in the future, but not now
    # try to rebind default ip, but not working :D
    # path1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # path2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # path1.bind((DEFAULT_IP, PORT))
    path2.bind((MOBILE_IP, PORT))

    # path1.connect((requested[0], int(requested[1])))
    path2.connect((REQUESTED_IP, int(REQUESTED_PORT)))

    # path1.sendall("GET / HTTP/1.1\r\n\r\n".encode('ascii'))
    path2.sendall("GET / HTTP/1.1\r\n\r\n".encode('ascii'))

    pass


def sendRangeRequest():
    contentLength = int(sendHead())
    connection1_load = 'bytes=0-' + str(int(contentLength / 4))
    connection2_load = 'bytes=' + str(int(contentLength / 4)) + '-' + str(contentLength)
    connection1 = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
    connection2 = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
    headers1 = {'Connection': 'Keep-Alive', 'Range': connection1_load}
    headers2 = {'Connection': 'Keep-Alive', 'Range': connection2_load}
    connection1.request("GET", "/" + REQUESTED_FILE, body=None, headers=headers1)
    connection2.request("GET", "/" + REQUESTED_FILE, body=None, headers=headers2)
    response1 = connection1.getresponse()
    response2 = connection2.getresponse()
    connection1.close()
    connection2.close()
    try:
        response = response1.read()
    except hc.IncompleteRead as e:
        response = e.partial
    try:
        response += response2.read()
    except hc.IncompleteRead as e:
        response += e.partial
    return response


def sendHeadDefault():
    con = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
    con.request("HEAD", "/" + REQUESTED_FILE, body=None)
    con.close()
    return con.getresponse()


def sendHeadSecond():
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.bind((MOBILE_IP, PORT))
    con.connect((REQUESTED_IP, REQUESTED_PORT))
    con.sendall("HEAD / HTTP/1.1\r\n\r\n".encode('ascii'))
    response = con.recv(2048).decode("utf-8").split("\r\n")
    responseDict = {}
    for line in response:
        if line.__contains__(":"):
            key = line.split(":")[0]
            value = line.split(":")[1][1:]
            responseDict[key] = value
    con.close()
    return responseDict


# send two head request to measure bandwidth
def sendHead():
    defaultResponse = sendHeadDefault()
    secondResponse = sendHeadSecond()
    return defaultResponse.getheader("content-length")


def assignRequestedPath(requested):
    global REQUESTED_IP
    REQUESTED_IP = requested.split(":")[0]
    global REQUESTED_PORT
    REQUESTED_PORT = requested.split(":")[1].split("/")[0]
    global REQUESTED_FILE
    REQUESTED_FILE = requested.split("/")[1]


def handleServerRequests(self):
    response = sendRangeRequest()
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    self.wfile.write(response)


def handleRequests(self):
    # TODO
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    # self.copyfile(ur.urlopen(self.path[1:]), self.wfile)


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/34.204.87.0:8080"):
            assignRequestedPath(self.path[1:])
            handleServerRequests(self)
            # tryTwoConnection()
        else:
            handleRequests(self)


# main connection
# Starts by default once program starts
connection = ThreadingHTTPServer((DEFAULT_IP, PORT), Proxy)
connection.serve_forever()
