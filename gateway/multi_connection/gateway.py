from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import datetime, timezone
from wsgiref.handlers import format_date_time
from time import mktime
import http.client as hc
import socket
import threading

WIFI_IP = '192.168.1.34'
MOBILE_IP = '192.168.43.38'
LAN_IP = '192.168.1.38'
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
PORT = 8080

REQUESTED_IP = ''
REQUESTED_PORT = 0
REQUESTED_FILE = ''

NOW = datetime.now(timezone.utc).timestamp()
startTimeDefault = NOW
serverTimeDefault = NOW
startTimeMobile = NOW
serverTimeMobile = NOW

headDefaultResponse = None
headMobileResponse = None
CONTENT_LENGTH = 0

RESPONSE_LTE = None
RESPONSE_WIFI = None


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


def useMobile(startByte, endByte):
    connectionLTE = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connectionLTE.bind((MOBILE_IP, PORT))
    connectionLTE.connect((REQUESTED_IP, int(REQUESTED_PORT)))
    connectionLTE.sendall(("GET / {} HTTP/1.1\r\nConnection: Keep-Alive\r\nRange: bytes={}-{}"
                         .format(REQUESTED_FILE, startByte, endByte).encode("ascii")))

    global RESPONSE_LTE
    RESPONSE_LTE = connectionLTE.recv(1024)  # should be string or byte?
    connectionLTE.close()


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

    global RESPONSE_WIFI
    RESPONSE_WIFI = response


def sendRangeRequest():
    return RESPONSE_WIFI + RESPONSE_LTE


# TODO differences are two close
# mobile is always faster, Kota?
# how to decide loads
def calculateLoadWeight():
    defaultStamp = serverTimeDefault - startTimeDefault
    mobileStamp = serverTimeMobile - startTimeMobile
    print('defaultStamp: ' + str(defaultStamp))
    print('mobileStamp: ' + str(mobileStamp))


# send two head request to measure bandwidth and get content length
def assignContentLength():
    global CONTENT_LENGTH
    CONTENT_LENGTH = headDefaultResponse.getheader("content-length")


# Send HEAD request over second connection
def sendHeadMobile():
    global startTimeMobile
    global serverTimeMobile
    global headMobileResponse
    con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    con.bind((MOBILE_IP, PORT))
    con.connect((REQUESTED_IP, int(REQUESTED_PORT)))
    startTimeMobile = getNow()
    con.sendall("HEAD / HTTP/1.1\r\n\r\n".encode('ascii'))
    response = con.recv(2048).decode("utf-8").split("\r\n")
    serverTimeMobile = getNow()
    responseDict = {}
    for line in response:
        if line.__contains__(":"):
            key = line.split(":")[0]
            value = line.split(":")[1][1:]
            responseDict[key] = value
    con.close()
    headMobileResponse = responseDict


# return current time as timestamp
def getNow():
    return datetime.now(timezone.utc).timestamp()


# Send HEAD request over default connection
def sendHeadDefault():
    global startTimeDefault
    global serverTimeDefault
    global headDefaultResponse
    con = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
    startTimeDefault = getNow()
    con.request("HEAD", "/" + REQUESTED_FILE, body=None)
    response = con.getresponse()
    serverTimeDefault = getNow()
    con.close()
    headDefaultResponse = response


# Send two HEAD requests using threads
def measureBandWidth():
    defaultThread = threading.Thread(target=sendHeadDefault)
    mobileThread = threading.Thread(target=sendHeadMobile)
    defaultThread.start()
    mobileThread.start()
    defaultThread.join(5000)
    mobileThread.join(5000)


# Assign requested ip, port and file path to global variables
def assignRequestedPath(requested):
    global REQUESTED_IP
    global REQUESTED_PORT
    global REQUESTED_FILE
    REQUESTED_IP = requested.split(":")[0]
    REQUESTED_PORT = requested.split(":")[1].split("/")[0]
    REQUESTED_FILE = requested.split("/")[1]


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/34.204.87.0:8080"):
            assignRequestedPath(self.path[1:])
            measureBandWidth()
            assignContentLength()
            calculateLoadWeight()
            response = sendRangeRequest()
            pushBackToClient(self, response)
        else:
            handleRequests(self)


# main connection
# Starts by default once program starts
connection = ThreadingHTTPServer((DEFAULT_IP, PORT), Proxy)
connection.serve_forever()
