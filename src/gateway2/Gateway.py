from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from gateway.TestServerHandler import TestServerHandler
from datetime import datetime, timezone
from wsgiref.handlers import format_date_time
import requests as req
from time import mktime
from socket import *
import threading
import ssl
import config.config as cfg

# init gateway info
GATEWAY_IP = cfg.primary['ip']
GATEWAY_PORT = cfg.primary['port']

# init test server info
TEST_SERVER_IP = cfg.server['ip']
TEST_SERVER_PORT = str(cfg.server['port'])

# init connection info
PRIMARY_IP = cfg.primary['ip']
PRIMARY_PORT = cfg.primary['port']
SECOND_IP = cfg.secondary['ip']
SECOND_PORT = cfg.secondary['port']
IS_SECOND_AVAILABLE = True

# init request info
REQUESTED_HOSTNAME = ''
REQUESTED_PATH = ''
REQUESTED_PORT = cfg.requested['httpPort']
HTTP_VERSION = cfg.requested['httpVersion']
IS_ACCEPT_RANGE = True
IS_VERIFY = False
CONTENT_LENGTH = 0
CONTENT_TYPE = ""

# init timestamps
CURRENT_TIME = datetime.now(timezone.utc).timestamp()
START_STAMP_PRIMARY = CURRENT_TIME
END_STAMP_PRIMARY = CURRENT_TIME
START_STAMP_SECOND = CURRENT_TIME
END_STAMP_SECOND = CURRENT_TIME

# init range boundaries
PRIMARY_RANGE_END = 0
SECOND_RANGE_START = 0

# init get request responses to keep them as bytes
RESPONSE_PRIMARY = b""
RESPONSE_SECOND = b""
RESPONSE = b""

# init head request response
HEAD_RESPONSE_HEADERS = None

# init socket request headers
SOCKET_HEAD_HEADERS = ""
SOCKET_GET_HEADERS = ""

# to create header
LINE = "\r\n"
HEADER = LINE + LINE


def handleRequest(self):
    assignRequestInfo(self.path[1:])
    createSocketHeadHeaders()
    measureBandwidth()
    assignContentInfo()
    calculateLoadWeight()
    createSocketGetHeaders()
    sendRangeRequest()
    pushBackToClient(self)


# Assign request info
# Requested string comes in the format of http://site/path or https://site/path
def assignRequestInfo(requested):
    global HTTP_VERSION, REQUESTED_PORT, REQUESTED_HOSTNAME, REQUESTED_PATH, IS_VERIFY
    HTTP_VERSION = requested.split(":")[0] + "://"
    if HTTP_VERSION.__contains__("s"):
        IS_VERIFY = True
        REQUESTED_PORT = cfg.requested['httpsPort']
    REQUESTED_HOSTNAME = requested.split("//")[1].split("/")[0]
    REQUESTED_PATH = '/'
    try:
        REQUESTED_PATH += requested.split("//")[1].split("/", 1)[1]
    except:
        print("no path was found")


# Create headers to send HEAD request over socket using Secondary Connection
def createSocketHeadHeaders():
    global SOCKET_HEAD_HEADERS
    SOCKET_HEAD_HEADERS = "HEAD " + REQUESTED_PATH + " HTTP/1.1" + LINE
    SOCKET_HEAD_HEADERS += "Host: " + REQUESTED_HOSTNAME + LINE
    SOCKET_HEAD_HEADERS += "Accept: */*" + LINE
    SOCKET_HEAD_HEADERS += "User-Agent: kibitzer" + LINE
    SOCKET_HEAD_HEADERS += "Connection: Close" + HEADER


# Measure bandwidth using HEAD requests over two connections
def measureBandwidth():
    defaultThread = threading.Thread(target=sendHeadPrimary)
    mobileThread = threading.Thread(target=sendHeadSecondary)
    defaultThread.start()
    mobileThread.start()
    defaultThread.join()
    mobileThread.join()


# Send HEAD request over Primary Connection
def sendHeadPrimary():
    global START_STAMP_PRIMARY, HEAD_RESPONSE_HEADERS, END_STAMP_PRIMARY
    START_STAMP_PRIMARY = getCurrentTime()
    HEAD_RESPONSE_HEADERS = req.head(HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH, verify=IS_VERIFY).headers
    END_STAMP_PRIMARY = getCurrentTime()


def getCurrentTime():
    return datetime.now(timezone.utc).timestamp()


# Send HEAD request over Secondary Connection
def sendHeadSecondary():
    global IS_SECOND_AVAILABLE
    try:
        con = socket(AF_INET, SOCK_STREAM)
        # TODO can be deleted, possible cause of delay
        con.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        con.bind((SECOND_IP, SECOND_PORT))
        if IS_VERIFY:
            sendHeadHttps(con)
        else:
            sendHeadHttp(con)
    except:
        print("second connection was not found")
        IS_SECOND_AVAILABLE = False


# Send HEAD request to HTTPS sources
def sendHeadHttps(con):
    global START_STAMP_SECOND, END_STAMP_SECOND
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    context.load_default_certs()
    ssl_socket = context.wrap_socket(con, server_hostname=REQUESTED_HOSTNAME)
    ssl_socket.connect((REQUESTED_HOSTNAME, REQUESTED_PORT))
    START_STAMP_SECOND = getCurrentTime()
    ssl_socket.sendall(SOCKET_HEAD_HEADERS.encode("utf-8"))
    ssl_socket.recv(1024)
    END_STAMP_SECOND = getCurrentTime()
    # TODO add shutdowns, any effects?
    ssl_socket.close()
    con.close()


# Send HEAD request to HTTP
def sendHeadHttp(con):
    global START_STAMP_SECOND, END_STAMP_SECOND
    con.connect((REQUESTED_HOSTNAME, REQUESTED_PORT))
    START_STAMP_SECOND = getCurrentTime()
    con.sendall(SOCKET_HEAD_HEADERS.encode('utf-8'))
    con.recv(1024)
    END_STAMP_SECOND = getCurrentTime()
    # TODO added shutdown, any effect??
    con.shutdown()
    con.close()


# Check HEAD request responses and assign content info
def assignContentInfo():
    global IS_ACCEPT_RANGE, CONTENT_LENGTH, CONTENT_TYPE
    try:
        if HEAD_RESPONSE_HEADERS["accept-ranges"].lower() == "none":
            IS_ACCEPT_RANGE = False
    except:
        print("accept ranges header was not found")
        IS_ACCEPT_RANGE = False
    try:
        CONTENT_LENGTH = int(HEAD_RESPONSE_HEADERS["content-length"])
    except:
        print("content length header was not found")
    try:
        CONTENT_TYPE = HEAD_RESPONSE_HEADERS["content-type"]
    except:
        print("content type header was not found")


# Calculate load weight over timestamps
def calculateLoadWeight():
    global PRIMARY_RANGE_END, SECOND_RANGE_START
    defaultStamp = END_STAMP_PRIMARY - START_STAMP_PRIMARY
    mobileStamp = END_STAMP_SECOND - START_STAMP_SECOND
    if mobileStamp != 0:
        defaultLoadRate = round((mobileStamp / (defaultStamp + mobileStamp)), 2)
    else:
        defaultLoadRate = 1
    PRIMARY_RANGE_END = round(defaultLoadRate * CONTENT_LENGTH)
    SECOND_RANGE_START = PRIMARY_RANGE_END + 1


# Create headers to send GET request over socket using Secondary Connection
def createSocketGetHeaders():
    global SOCKET_GET_HEADERS
    SOCKET_GET_HEADERS = "GET " + REQUESTED_PATH + " HTTP/1.1" + LINE
    SOCKET_GET_HEADERS += "Host: " + REQUESTED_HOSTNAME + LINE
    SOCKET_GET_HEADERS += "Accept: */*" + LINE
    SOCKET_GET_HEADERS += "User-Agent: kibitzer" + LINE
    SOCKET_GET_HEADERS += "Range: bytes=" + str(SECOND_RANGE_START) + "-" + LINE
    SOCKET_GET_HEADERS += "Connection: Keep-Alive" + HEADER


# Send GET requests over two connection as Range Requests
def sendRangeRequest():
    global RESPONSE
    defaultThread = threading.Thread(target=sendGetPrimary)
    if IS_SECOND_AVAILABLE and IS_ACCEPT_RANGE:
        mobileThread = threading.Thread(target=sendGetSecondary)
    defaultThread.start()
    if IS_SECOND_AVAILABLE and IS_ACCEPT_RANGE:
        mobileThread.start()  # TODO check
    defaultThread.join()
    if IS_SECOND_AVAILABLE and IS_ACCEPT_RANGE:
        mobileThread.join()
    RESPONSE = RESPONSE_PRIMARY + RESPONSE_SECOND


# Send GET request over Primary Connection
def sendGetPrimary():
    global RESPONSE_PRIMARY
    headers = {
        "Host": REQUESTED_HOSTNAME, "Accept": "*/*",
        "User-Agent": "kibitzer", 'Connection': 'Close'
    }
    if IS_ACCEPT_RANGE:
        rangeValue = 'bytes=0-' + str(PRIMARY_RANGE_END)
        headers.update({'Range': rangeValue})

    RESPONSE_PRIMARY = req.get(HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH,
                               headers=headers, verify=True).content


# Send GET request over Secondary Connection
def sendGetSecondary():
    global RESPONSE_SECOND
    con = socket(AF_INET, SOCK_STREAM)
    con.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    con.bind((SECOND_IP, SECOND_PORT + 1))
    if IS_VERIFY:
        sendGetHttps(con)
    else:
        sendGetHttp(con)


# Send GET request to HTTPS
def sendGetHttps(con):
    global RESPONSE_SECOND
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    context.load_default_certs()
    ssl_socket = context.wrap_socket(con, server_hostname=REQUESTED_HOSTNAME)
    ssl_socket.connect((REQUESTED_HOSTNAME, REQUESTED_PORT))
    ssl_socket.sendall(SOCKET_GET_HEADERS.encode("utf-8"))
    isBody = False
    while True:
        data = ssl_socket.recv(102400)
        if not data:
            break
        if isBody:
            RESPONSE_SECOND += data
        isBody = True
    # TODO try shutdown
    ssl_socket.close()
    con.close()


# Send GET request to HTTP
def sendGetHttp(con):
    global RESPONSE_SECOND
    con.connect((REQUESTED_HOSTNAME, REQUESTED_PORT))
    con.sendall(SOCKET_GET_HEADERS.encode("utf-8"))
    isBody = False
    while True:
        data = con.recv(102400)
        if not data:
            break
        if isBody:
            RESPONSE_SECOND += data
        isBody = True
    con.close()


# Push back GET request responses to client
def pushBackToClient(self):
    # TODO modify and add headers from range requests' responses
    self.send_response(200)
    self.send_header('Content-Type', CONTENT_TYPE)
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Content-Length', str(CONTENT_LENGTH))
    self.end_headers()
    self.wfile.write(RESPONSE)


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/" + TEST_SERVER_IP + ":" + TEST_SERVER_PORT):
            TestServerHandler(self)
        elif self.path.startswith("/http"):
            handleRequest(self)
        else:
            # TODO implement error 404, 500 vs
            pass


connection = ThreadingHTTPServer((GATEWAY_IP, GATEWAY_PORT), Proxy)
connection.serve_forever()
