import http.client as hc
import socket
from datetime import datetime, timezone
import threading
import time
from wsgiref.handlers import format_date_time
from time import mktime
import email.utils as eut
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

WIFI_IP = '192.168.1.34'
MOBILE_IP = '192.168.43.38'
LAN_IP = '192.168.1.38'
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
PORT = 8080

REQUESTED_IP = ''
REQUESTED_PORT = 0
REQUESTED_FILE = ''

startTimeDefault = 0
serverTimeDefault = 0
startTimeMobile = 0
serverTimeMobile = 0

headDefaultResponse = None
headMobileResponse = None
CONTENT_LENGTH = 0


# Handle Request that are not going to Test Server
# Act like usual proxy server
# Try Hybrid connection
def handleRequests(self):
    # TODO
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.end_headers()
    # self.copyfile(ur.urlopen(self.path[1:]), self.wfile)


def getTime():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


def pushBackToClient(self, response):
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Date', getTime())
    self.end_headers()
    self.wfile.write(response)


def useMobile():
    path2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    path2.bind((MOBILE_IP, PORT))
    path2.connect((REQUESTED_IP, int(REQUESTED_PORT)))
    path2.sendall("GET / HTTP/1.1\r\n\r\n".encode('ascii'))
    return ""


def useDefault(endByte):
    connectionLoad = 'bytes=0-' + endByte
    con = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
    headers = {'Connection': 'Keep-Alive', 'Range': connectionLoad}
    con.request("GET", "/" + REQUESTED_FILE, body=None, headers=headers)
    response1 = con.getresponse()
    con.close()
    try:
        response = response1.read()
    except hc.IncompleteRead as e:
        response = e.partial
    return response


def sendRangeRequest():
    responseDefault = useDefault("")
    responseMobile = useMobile()
    # TODO concat responses and return
    return responseDefault + responseMobile


def calculateLoadWeight():
    pass


# TODO implement like sendHeadDefault
# Send HEAD request over second connection
def sendHeadMobile():
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


# Send HEAD request over default connection
def sendHeadDefault():
    con = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
    global startTimeDefault
    stamp = mktime(datetime.now().timetuple())
    startTimeDefault = format_date_time(stamp)
    con.request("HEAD", "/" + REQUESTED_FILE, body=None)
    response = con.getresponse()
    con.close()
    global headDefaultResponse
    headDefaultResponse = response


# TODO implement threading
# send two head request to measure bandwidth
def getContentLength():
    sendHeadDefault()
    sendHeadMobile()
    global serverTimeDefault
    serverTimeDefault = headDefaultResponse.getheader("date")
    global serverTimeMobile
    serverTimeMobile = headMobileResponse.getheader("date")
    global CONTENT_LENGTH
    CONTENT_LENGTH = headDefaultResponse.getheader("content-length")


# Assign requested ip, port and file path to global variables
def assignRequestedPath(requested):
    global REQUESTED_IP
    REQUESTED_IP = requested.split(":")[0]
    global REQUESTED_PORT
    REQUESTED_PORT = requested.split(":")[1].split("/")[0]
    global REQUESTED_FILE
    REQUESTED_FILE = requested.split("/")[1]


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/34.204.87.0:8080"):
            assignRequestedPath(self.path[1:])
            getContentLength()
            response = sendRangeRequest()
            pushBackToClient(self, response)
        else:
            handleRequests(self)


# main connection
# Starts by default once program starts
connection = ThreadingHTTPServer((DEFAULT_IP, PORT), Proxy)
connection.serve_forever()
