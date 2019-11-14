import http.client as hc
import threading as th
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, SimpleHTTPRequestHandler

WIFI_ADDRESS = '10.200.113.100'
LAN_ADDRESS = '192.168.1.38'
SERVER_ADDRESS = '172.31.84.69'
ADDRESS = WIFI_ADDRESS


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


def send_RangeRequest(requested, contentLength):
    # newConnectionThread = th.Thread(target=do_Thread_Connection, args=())
    # newConnectionThread.start()

    # TODO implement threading
    connection1_load = 'bytes=0-' + str(int(contentLength / 4))
    connection2_load = 'bytes=' + str(int(contentLength / 4)) + '-' + str(contentLength)
    connection1 = hc.HTTPConnection(requested[0], requested[1])
    connection2 = hc.HTTPConnection(requested[0], requested[1])
    headers1 = {'Connection': 'Keep-Alive', 'Range': connection1_load}
    headers2 = {'Connection': 'Keep-Alive', 'Range': connection2_load}
    connection1.request("GET", "/" + requested[2], body=None, headers=headers1)
    connection2.request("GET", "/" + requested[2], body=None, headers=headers2)
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


def send_HEAD(requested):
    connection = hc.HTTPConnection(requested[0], requested[1])
    connection.request("HEAD", "/" + requested[2], body=None)
    response = connection.getresponse()
    connection.close()
    return response.getheader("content-length")


def getRequested_URL(requested):
    host = requested.split(":")[0]
    port = requested.split(":")[1].split("/")[0]
    path = requested.split("/")[1]
    return host, port, path


def handleServerRequest(self):
    requested = getRequested_URL(self.path[1:])
    contentLength = send_HEAD(requested)
    response = send_RangeRequest(requested, int(contentLength))
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
        print(self.path)
        if self.path.startswith("/34.204.87.0:8080"):
            handleServerRequest(self)
        else:
            handleRequests(self)


# main connection
# Starts by default once program starts
wifi = ThreadingHTTPServer((ADDRESS, 8080), Proxy)
wifi.serve_forever()
