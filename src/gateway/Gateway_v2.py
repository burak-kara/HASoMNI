from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from requests_toolbelt.adapters.source import SourceAddressAdapter
from datetime import datetime, timezone
import config.config as cfg
import requests as req
import logging as log
from socket import *
import threading
import ssl

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
REQUEST_RECV_TIME = CURRENT_TIME
REQUEST_HANDLE_TIME = CURRENT_TIME

# init range boundaries
PRIMARY_RANGE_START = 0
PRIMARY_RANGE_END = 0
SECOND_RANGE_START = 0
SECOND_RANGE_END = 0
SECOND_LOAD = 0
SEGMENT_SIZE = 0

# init get request responses to keep them as bytes
RESPONSE_PRIMARY = b""
RESPONSE_SECOND = b""
RESPONSE = b""

# init head request response
HEAD_RESPONSE_HEADERS = None

# init socket request headers
SOCKET_HEAD_HEADERS = ""
SOCKET_GET_HEADERS = ""

# constants to create headers
LINE = "\r\n"
HEADER = LINE + LINE

# TODO delete
TOTAL = 0


def handleRequest(self):
    assignRequestInfo(self.path[1:])
    createSocketHeadHeaders()
    measureBandwidth()
    assignContentInfo()
    log.info("++++ Head requests are done ++++")
    getRequestedSource(self)


# Assign request info
# Requested string comes in the format of http://site/path or https://site/path
def assignRequestInfo(requested):
    global HTTP_VERSION, REQUESTED_PORT, REQUESTED_HOSTNAME, REQUESTED_PATH, IS_VERIFY
    HTTP_VERSION = requested.split(":")[0] + "://"
    if HTTP_VERSION.__contains__("s"):
        IS_VERIFY = True
        REQUESTED_PORT = cfg.requested['httpsPort']
    REQUESTED_HOSTNAME = requested.split("//")[1].split("/")[0]
    if REQUESTED_HOSTNAME.__contains__(":"):
        REQUESTED_HOSTNAME = REQUESTED_HOSTNAME.split(":")[0]
        REQUESTED_PORT = 8080
    REQUESTED_PATH = '/'
    try:
        REQUESTED_PATH += requested.split("//")[1].split("/", 1)[1]
    except:
        log.error("No path was found")


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
    log.info("*** Primary head is started")
    global START_STAMP_PRIMARY, HEAD_RESPONSE_HEADERS, END_STAMP_PRIMARY
    START_STAMP_PRIMARY = getCurrentTime()
    if REQUESTED_PORT == 8080:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + ":8080" + REQUESTED_PATH
    else:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH
    HEAD_RESPONSE_HEADERS = req.head(URL, verify=IS_VERIFY)
    END_STAMP_PRIMARY = getCurrentTime()
    HEAD_RESPONSE_HEADERS = HEAD_RESPONSE_HEADERS.headers
    log.info("*** Primary head is done")


# Send HEAD request over Secondary Connection
def sendHeadSecondary():
    log.info("--- Secondary head is started")
    global IS_SECOND_AVAILABLE
    try:
        con = socket(AF_INET, SOCK_STREAM)
        con.bind((SECOND_IP, SECOND_PORT))
        if IS_VERIFY:
            sendHeadSecondaryHttps(con)
        else:
            sendHeadSecondaryHttp(con)
        log.info("--- Secondary head is done")
    except:
        log.info("--- Second connection was not found")
        IS_SECOND_AVAILABLE = False


# Send HEAD request to HTTPS sources
def sendHeadSecondaryHttps(con):
    global START_STAMP_SECOND, END_STAMP_SECOND
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = True
    context.load_default_certs()
    ssl_socket = context.wrap_socket(con, server_hostname=REQUESTED_HOSTNAME)
    ssl_socket.connect((REQUESTED_HOSTNAME, REQUESTED_PORT))
    START_STAMP_SECOND = getCurrentTime()
    ssl_socket.sendall(SOCKET_HEAD_HEADERS.encode("utf-8"))
    ssl_socket.recv(10)
    END_STAMP_SECOND = getCurrentTime()
    ssl_socket.close()
    con.close()


# Send HEAD request to HTTP
def sendHeadSecondaryHttp(con):
    global START_STAMP_SECOND, END_STAMP_SECOND
    con.connect((REQUESTED_HOSTNAME, REQUESTED_PORT))
    START_STAMP_SECOND = getCurrentTime()
    con.sendall(SOCKET_HEAD_HEADERS.encode('utf-8'))
    con.recv(10)
    END_STAMP_SECOND = getCurrentTime()
    con.close()


# Check HEAD request responses and assign content info
def assignContentInfo():
    global IS_ACCEPT_RANGE, CONTENT_LENGTH, CONTENT_TYPE
    try:
        if HEAD_RESPONSE_HEADERS["accept-ranges"].lower() == "none":
            IS_ACCEPT_RANGE = False
    except:
        log.error("Accept-Range header was not found")
        IS_ACCEPT_RANGE = False
    try:
        CONTENT_LENGTH = int(HEAD_RESPONSE_HEADERS["content-length"])
    except:
        log.error("Content-Length header was not found")
    try:
        CONTENT_TYPE = HEAD_RESPONSE_HEADERS["content-type"]
    except:
        log.error("Content-Type header was not found")


def getRequestedSource(self):
    global PRIMARY_RANGE_START, PRIMARY_RANGE_END, SECOND_RANGE_START, SECOND_RANGE_END, SECOND_LOAD, SEGMENT_SIZE, RESPONSE, RESPONSE_PRIMARY
    SEGMENT_SIZE = int(CONTENT_LENGTH / 10)
    segments = list(range(0, CONTENT_LENGTH + 1, SEGMENT_SIZE))
    # print(segments)
    # print(SEGMENT_SIZE)
    # print(SEGMENT_SIZE * 10)
    # print(CONTENT_LENGTH)
    defaultLW, secondaryLW = getLoadWeights()

    headers = {
        "Host": REQUESTED_HOSTNAME, "Accept": "*/*",
        "User-Agent": "kibitzer", 'Connection': 'Close'
    }

    if REQUESTED_PORT == 8080:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + ":8080" + REQUESTED_PATH
    else:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH

    for i in range(0, 10):
        # print("-------" + str(i))
        PRIMARY_RANGE_START = segments[i]
        PRIMARY_RANGE_END = segments[i] + round(defaultLW * SEGMENT_SIZE) - 1
        # print("pr start: " + str(PRIMARY_RANGE_START))
        # print("pr end: " + str(PRIMARY_RANGE_END))
        SECOND_RANGE_START = PRIMARY_RANGE_END + 1
        SECOND_RANGE_END = segments[i + 1] - 1
        SECOND_LOAD = SECOND_RANGE_END - SECOND_RANGE_START
        # print("sc start: " + str(SECOND_RANGE_START))
        # print("sc end: " + str(SECOND_RANGE_END))
        log.info("*** Primary load length: %s bytes / %s MB", str(PRIMARY_RANGE_END - PRIMARY_RANGE_START),
                 str(round(convertToMb(PRIMARY_RANGE_END - PRIMARY_RANGE_START), 2)))
        log.info("--- Secondary load length: %s bytes / %s MB", str(SECOND_RANGE_END - SECOND_RANGE_START),
                 str(round(convertToMb(SECOND_RANGE_END - SECOND_RANGE_START), 2)))

        if IS_ACCEPT_RANGE:
            rangeValue = 'bytes=' + str(PRIMARY_RANGE_START) + '-' + str(PRIMARY_RANGE_END)
            headers.update({'Range': rangeValue})
            print("rangeValue")
            print(rangeValue)   
        RESPONSE_PRIMARY = req.get(URL, headers=headers, verify=True)
        RESPONSE = RESPONSE_PRIMARY.content
        print(RESPONSE_PRIMARY.headers['Content-Range'])
        print(RESPONSE_PRIMARY.headers['Content-Length'])
        # print(RESPONSE_PRIMARY.status_code)
        print("bytes " + str(PRIMARY_RANGE_START) + "-" + str(PRIMARY_RANGE_END) + "/" + str(CONTENT_LENGTH))
        print(SEGMENT_SIZE)
        # sendRangeRequest()
        # pushBackToClient(self)
        global REQUEST_HANDLE_TIME
        self.send_response(206)
        self.send_header('Accept-Ranges', "bytes")
        self.send_header('Content-Type', CONTENT_TYPE)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Range',
                         "bytes " + str(PRIMARY_RANGE_START) + "-" + str(PRIMARY_RANGE_END) + "/" + str(CONTENT_LENGTH))
        self.send_header('Content-Length', str(SEGMENT_SIZE))

        self.end_headers()
        self.wfile.write(RESPONSE)
        # self.wfile.write(bytearray("asdasd", 'utf-8'))
        log.info("Response is pushed back to client")
        REQUEST_HANDLE_TIME = getCurrentTime()
        log.info("Total time passed: %s seconds", str(round(REQUEST_HANDLE_TIME - REQUEST_RECV_TIME, 2)))
        RESPONSE_PRIMARY = b""
        RESPONSE = b""
        print("-------------------------------------------------------------------------------------------")


# Calculate load weights
def getLoadWeights():
    primaryStamp = END_STAMP_PRIMARY - START_STAMP_PRIMARY
    secondaryStamp = END_STAMP_SECOND - START_STAMP_SECOND
    log.info("*** Primary stamp: %s", str(round(primaryStamp, 2)))
    log.info("--- Secondary stamp: %s", str(round(secondaryStamp, 2)))
    log.info("Content-Length: %s", str(CONTENT_LENGTH))
    if secondaryStamp != 0:
        defaultLoadRate = round((secondaryStamp / (primaryStamp + secondaryStamp)), 2)
    else:
        defaultLoadRate = 1
    return defaultLoadRate, 1 - defaultLoadRate


# Send GET requests over two connection as Range Requests
def sendRangeRequest():
    global RESPONSE
    defaultThread = threading.Thread(target=sendGetPrimary)
    if IS_SECOND_AVAILABLE and IS_ACCEPT_RANGE:
        mobileThread = threading.Thread(target=sendGetSecondary)
        mobileThread.start()
    defaultThread.start()
    defaultThread.join()
    if IS_SECOND_AVAILABLE and IS_ACCEPT_RANGE:
        mobileThread.join()
    print("----------------")
    RESPONSE = RESPONSE_PRIMARY + RESPONSE_SECOND


# Send GET request over Primary Connection
def sendGetPrimary():
    log.info("*** Primary GET is started")
    global RESPONSE_PRIMARY
    headers = {
        "Host": REQUESTED_HOSTNAME, "Accept": "*/*",
        "User-Agent": "kibitzer", 'Connection': 'Close'
    }
    if IS_ACCEPT_RANGE:
        rangeValue = 'bytes=' + str(PRIMARY_RANGE_START) + '-' + str(PRIMARY_RANGE_END)
        headers.update({'Range': rangeValue})
    if REQUESTED_PORT == 8080:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + ":8080" + REQUESTED_PATH
    else:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH
    RESPONSE_PRIMARY = req.get(URL,
                               headers=headers, verify=True).content
    log.info("*** Primary GET is done")


# Send GET request over Secondary Connection
def sendGetSecondary():
    log.info("--- Secondary GET is started")
    global RESPONSE_SECOND
    headers = {
        "Host": REQUESTED_HOSTNAME, "Accept": "*/*",
        "User-Agent": "kibitzer", 'Connection': 'Close'
    }
    if IS_ACCEPT_RANGE:
        rangeValue = "bytes=" + str(SECOND_RANGE_START) + "-" + str(SECOND_RANGE_END)
        headers.update({'Range': rangeValue})
    if REQUESTED_PORT == 8080:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + ":8080" + REQUESTED_PATH
    else:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH
    s = req.Session()
    s.mount('http://', SourceAddressAdapter(SECOND_IP))
    RESPONSE_SECOND = s.get(URL, headers=headers, verify=True).content

    log.info("--- Secondary GET is done")


# Push back GET request responses to client
def pushBackToClient(self):
    global REQUEST_HANDLE_TIME
    self.send_response(206)
    self.send_header('Content-Type', CONTENT_TYPE)
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Content-Range', "bytes " + str(SEGMENT_SIZE) + "/" + str(CONTENT_LENGTH))
    self.send_header('Content-Length', str(SEGMENT_SIZE))
    self.end_headers()
    self.wfile.write(RESPONSE)
    # self.wfile.write(bytearray("asdasd", 'utf-8'))
    log.info("Response is pushed back to client")
    REQUEST_HANDLE_TIME = getCurrentTime()
    log.info("Total time passed: %s seconds", str(round(REQUEST_HANDLE_TIME - REQUEST_RECV_TIME, 2)))


def getCurrentTime():
    return datetime.now(timezone.utc).timestamp()


def convertToMb(num):
    return num / (1024 * 1024)


class Proxy(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        global REQUEST_RECV_TIME
        if self.path.startswith("/http"):
            log.info("Gateway got a new request")
            REQUEST_RECV_TIME = getCurrentTime()
            handleRequest(self)
            log.info("---------------------------------------------------------------------\n")
        else:
            log.error("Undefined format")


log.basicConfig(filename='D:\\PyCharm Projects\\Senior\\src\\log_records\\gateway_v2.log', level=log.DEBUG,
                format='%(asctime)s - %(message)s')
connection = ThreadingHTTPServer((GATEWAY_IP, GATEWAY_PORT), Proxy)
connection.serve_forever()
