from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import datetime, timezone
from wsgiref.handlers import format_date_time
from time import mktime
import http.client as hc
from socket import *
import threading

WIFI_IP = '192.168.1.34'
MOBILE_IP = '192.168.43.38'
LAN_IP = '192.168.1.38'
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
DEFAULT_PORT = 8080
MOBILE_PORT = 8081

REQUESTED_IP = ''
REQUESTED_PORT = 0
REQUESTED_FILE = ''

NOW = datetime.now(timezone.utc).timestamp()
startTimeDefault = NOW
serverTimeDefault = NOW
startTimeMobile = NOW
serverTimeMobile = NOW

DEFAULT_RANGE_END = 0
MOBILE_RANGE_START = 0
CONTENT_LENGTH = 0
CONTENT_TYPE = ""

RESPONSE_DEFAULT_HEAD = None
RESPONSE_DEFAULT = b""
RESPONSE_MOBILE = b""
RESPONSE = b""

LINE = "\r\n"
HEADER = LINE + LINE


def getTime():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


def pushBackToClient(self):
    self.send_response(200)
    self.send_header('Content-type', CONTENT_TYPE)
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Date', getTime())
    self.end_headers()
    self.wfile.write(RESPONSE)


def useMobile():
    global RESPONSE_MOBILE
    con = socket(AF_INET, SOCK_STREAM)
    con.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    con.bind((MOBILE_IP, MOBILE_PORT + 1))
    con.connect((REQUESTED_IP, REQUESTED_PORT))
    request = "GET /" + REQUESTED_FILE + " HTTP/1.1" + LINE
    request += "Connection: close" + LINE
    request += "Range: bytes=" + str(MOBILE_RANGE_START) + "-" + str(CONTENT_LENGTH) + HEADER
    con.sendall(request.encode("ascii"))
    while True:
        data = con.recv(2048)
        if not data:
            break
        RESPONSE_MOBILE += data
    con.close()
    RESPONSE_MOBILE = RESPONSE_MOBILE.split(HEADER.encode("utf-8"), 1)[1]


def useDefault():
    global RESPONSE_DEFAULT
    rangeValue = 'bytes=0-' + str(DEFAULT_RANGE_END)
    headers = {'Connection': 'Keep-Alive', 'Range': rangeValue}
    con = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
    con.request("GET", "/" + REQUESTED_FILE, body=None, headers=headers)
    response = con.getresponse()
    con.close()
    try:
        RESPONSE_DEFAULT = response.read()
    except hc.IncompleteRead as e:
        RESPONSE_DEFAULT = e.partial


def sendRangeRequest():
    global RESPONSE
    defaultThread = threading.Thread(target=useDefault)
    mobileThread = threading.Thread(target=useMobile)
    defaultThread.start()
    mobileThread.start()
    defaultThread.join()
    mobileThread.join()
    RESPONSE = RESPONSE_DEFAULT + RESPONSE_MOBILE


def calculateLoadWeight():
    global DEFAULT_RANGE_END, MOBILE_RANGE_START
    defaultStamp = serverTimeDefault - startTimeDefault
    mobileStamp = serverTimeMobile - startTimeMobile
    if mobileStamp != 0:
        defaultLoadRate = round((mobileStamp / (defaultStamp + mobileStamp)), 2)
    else:
        defaultLoadRate = 1
    DEFAULT_RANGE_END = round(defaultLoadRate * CONTENT_LENGTH)
    MOBILE_RANGE_START = DEFAULT_RANGE_END
    print("Default: " + str(DEFAULT_RANGE_END) + "/" + str(CONTENT_LENGTH))


def assignContentInfo():
    global CONTENT_LENGTH, CONTENT_TYPE
    CONTENT_LENGTH = int(RESPONSE_DEFAULT_HEAD.getheader("content-length"))
    CONTENT_TYPE = RESPONSE_DEFAULT_HEAD.getheader("content-type")


# Send HEAD request over second connection
def sendHeadMobile():
    global startTimeMobile, serverTimeMobile
    con = socket(AF_INET, SOCK_STREAM)
    con.bind((MOBILE_IP, MOBILE_PORT))
    con.connect((REQUESTED_IP, REQUESTED_PORT))
    request = "HEAD / HTTP/1.1" + LINE
    request += "Connection: close" + HEADER
    startTimeMobile = getNow()
    con.sendall(request.encode('ascii'))
    con.recv(2048)
    serverTimeMobile = getNow()
    con.close()


# return current time as timestamp
def getNow():
    return datetime.now(timezone.utc).timestamp()


# Send HEAD request over default connection
def sendHeadDefault():
    global startTimeDefault, serverTimeDefault, RESPONSE_DEFAULT_HEAD
    con = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
    startTimeDefault = getNow()
    con.request("HEAD", "/" + REQUESTED_FILE, body=None)
    response = con.getresponse()
    serverTimeDefault = getNow()
    con.close()
    RESPONSE_DEFAULT_HEAD = response


# Send two HEAD requests using threads
def measureBandWidth():
    defaultThread = threading.Thread(target=sendHeadDefault)
    mobileThread = threading.Thread(target=sendHeadMobile)
    defaultThread.start()
    mobileThread.start()
    defaultThread.join()
    mobileThread.join()


# Assign requested ip, port and file path to global variables
def assignRequestedPath(requested):
    global REQUESTED_IP, REQUESTED_PORT, REQUESTED_FILE
    REQUESTED_IP = requested.split(":")[0]
    REQUESTED_PORT = int(requested.split(":")[1].split("/")[0])
    REQUESTED_FILE = requested.split("/")[1]


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/3.134.95.115:8080"):
            assignRequestedPath(self.path[1:])
            measureBandWidth()
            assignContentInfo()
            calculateLoadWeight()
            sendRangeRequest()
            pushBackToClient(self)
        else:
            # TODO implement
            assignRequestedPath(self.path[1:])
            measureBandWidth()
            assignContentInfo()
            calculateLoadWeight()
            sendRangeRequest()
            pushBackToClient(self)


# main connection
# Starts by default once program starts
connection = ThreadingHTTPServer((DEFAULT_IP, DEFAULT_PORT), Proxy)
connection.serve_forever()
