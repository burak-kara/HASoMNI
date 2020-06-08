from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from requests_toolbelt.adapters.source import SourceAddressAdapter
from datetime import datetime, timezone
import config.config as cfg
import requests as req
import logging as log
import threading
import pycurl
from io import BytesIO
import netifaces
import psutil

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
REQUEST_RANGE = ''
IS_ACCEPT_RANGE = True
IS_VERIFY = False
CONTENT_LENGTH = 0
CONTENT_TYPE = ""
START = ''
END = ''

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
COUNTER = 0


def handleRequest(self):
    assignRequestInfo(self.path[1:], self.headers)
    createSocketHeadHeaders()
    measureBandwidth()
    assignContentInfo()
    log.info("++++ Head requests are done ++++")
    assignLoadWeights()
    sendRangeRequest()
    pushBackToClient(self)


# Assign request info
# Requested string comes in the format of http://site/path or https://site/path
def assignRequestInfo(requested, headers):
    global HTTP_VERSION, REQUESTED_PORT, REQUESTED_HOSTNAME, REQUESTED_PATH, IS_VERIFY, REQUEST_RANGE
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
    if headers is not None and headers.get('Range'):
        REQUEST_RANGE = headers.get('Range')


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
    defaultThread = threading.Thread(target=sendHeadPrimary, daemon=True)
    mobileThread = threading.Thread(target=sendHeadSecondary, daemon=True)
    defaultThread.start()
    mobileThread.start()
    defaultThread.join()
    mobileThread.join()


# Send HEAD request over Primary Connection
def sendHeadPrimary():
    log.info("*** Primary head is started")
    global START_STAMP_PRIMARY, HEAD_RESPONSE_HEADERS, END_STAMP_PRIMARY
    if REQUESTED_PORT == 8080:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + ":8080" + REQUESTED_PATH
    else:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH
    START_STAMP_PRIMARY = getCurrentTime()
    HEAD_RESPONSE_HEADERS = req.head(URL)
    END_STAMP_PRIMARY = getCurrentTime()
    HEAD_RESPONSE_HEADERS = HEAD_RESPONSE_HEADERS.headers
    log.info("*** Primary head is done")


# Send HEAD request over Secondary Connection
def sendHeadSecondary():
    log.info("--- Secondary head is started")
    global IS_SECOND_AVAILABLE, START_STAMP_SECOND, END_STAMP_SECOND
    try:
        if REQUESTED_PORT == 8080:
            URL = HTTP_VERSION + REQUESTED_HOSTNAME + ":8080" + REQUESTED_PATH
        else:
            URL = HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH
        START_STAMP_SECOND = getCurrentTime()

        s = req.Session()
        s.mount('http://', SourceAddressAdapter(SECOND_IP))
        x = s.head(URL)
        END_STAMP_SECOND = getCurrentTime()
        log.info("--- Secondary head is done")
    except:
        log.info("--- Second connection was not found")
        IS_SECOND_AVAILABLE = False


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


# Calculate load weights
def assignLoadWeights():
    global PRIMARY_RANGE_START, PRIMARY_RANGE_END, SECOND_RANGE_START, SECOND_RANGE_END, SECOND_LOAD, SEGMENT_SIZE
    global START, END
    primaryStamp = END_STAMP_PRIMARY - START_STAMP_PRIMARY
    secondaryStamp = END_STAMP_SECOND - START_STAMP_SECOND
    log.info("*** Primary stamp: %s", str(round(primaryStamp, 2)))
    log.info("--- Secondary stamp: %s", str(round(secondaryStamp, 2)))
    log.info("Content-Length: %s", str(CONTENT_LENGTH))
    SEGMENT_SIZE = int(CONTENT_LENGTH / 10)
    if secondaryStamp >= 0:
        defaultLoadRate = round((secondaryStamp / (primaryStamp + secondaryStamp)), 2)
        # TODO change
        # defaultLoadRate = 0.7
    else:
        defaultLoadRate = 1

    START, END = REQUEST_RANGE.split("=")[1].split('-')
    START = int(START)

    if END:
        END = int(END)
    else:
        END = START + SEGMENT_SIZE
        if END >= CONTENT_LENGTH:
            END = CONTENT_LENGTH - 1

    PRIMARY_RANGE_START = START
    PRIMARY_RANGE_END = START + round(defaultLoadRate * SEGMENT_SIZE) - 1
    SECOND_RANGE_START = PRIMARY_RANGE_END + 1
    SECOND_RANGE_END = END
    SECOND_LOAD = SECOND_RANGE_END - SECOND_RANGE_START
    log.info("*** Primary load length: %s bytes / %s MB", str(PRIMARY_RANGE_END - PRIMARY_RANGE_START),
             str(round(convertToMb(PRIMARY_RANGE_END - PRIMARY_RANGE_START), 2)))
    log.info("--- Secondary load length: %s bytes / %s MB", str(SECOND_RANGE_END - SECOND_RANGE_START),
             str(round(convertToMb(SECOND_RANGE_END - SECOND_RANGE_START), 2)))


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
    RESPONSE = RESPONSE_PRIMARY + RESPONSE_SECOND


# Send GET request over Primary Connection
def sendGetPrimary():
    global RESPONSE_PRIMARY
    log.info("*** Primary GET is started")
    # headers = {
    #     "Host": REQUESTED_HOSTNAME, "Accept": "*/*",
    #     "User-Agent": "kibitzer", 'Connection': 'Close'
    # }
    # if IS_ACCEPT_RANGE:
    #     rangeValue = 'bytes=' + str(PRIMARY_RANGE_START) + '-' + str(PRIMARY_RANGE_END)
    #     headers.update({'Range': rangeValue})
    # if REQUESTED_PORT == 8080:
    #     URL = HTTP_VERSION + REQUESTED_HOSTNAME + ":8080" + REQUESTED_PATH
    # else:
    #     URL = HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH
    # RESPONSE_PRIMARY = req.get(URL,
    #                            headers=headers).content

    headers = []
    if IS_ACCEPT_RANGE:
        rangeValue = 'bytes=' + str(PRIMARY_RANGE_START) + '-' + str(PRIMARY_RANGE_END)
        headers = ['Host: ' + REQUESTED_HOSTNAME, 'Accept: */*', 'User-Agent: kibitzer', 'Connection: Close',
                   'Range: ' + rangeValue]
    if REQUESTED_PORT == 8080:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + ":8080" + REQUESTED_PATH
    else:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH

    conn = pycurl.Curl()
    buffer = BytesIO()
    conn.setopt(pycurl.URL, URL)
    conn.setopt(pycurl.HTTPHEADER, headers)
    conn.setopt(pycurl.WRITEFUNCTION, buffer.write)
    conn.setopt(pycurl.INTERFACE, PRIMARY_IP)
    conn.perform()
    resp = buffer.getvalue()
    buffer.close()
    conn.close()
    RESPONSE_PRIMARY = resp
    log.info("*** Primary GET is done")


# Send GET request over Secondary Connection
def sendGetSecondary():
    log.info("--- Secondary GET is started")
    global RESPONSE_SECOND
    headers = []
    if IS_ACCEPT_RANGE:
        rangeValue = "bytes=" + str(SECOND_RANGE_START) + "-" + str(SECOND_RANGE_END)
        headers = ['Host: ' + REQUESTED_HOSTNAME, 'Accept: */*', 'User-Agent: kibitzer', 'Connection: Close',
                   'Range: ' + rangeValue]
    if REQUESTED_PORT == 8080:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + ":8080" + REQUESTED_PATH
    else:
        URL = HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH

    conn = pycurl.Curl()
    buffer = BytesIO()
    conn.setopt(pycurl.URL, URL)
    conn.setopt(pycurl.HTTPHEADER, headers)
    conn.setopt(pycurl.WRITEFUNCTION, buffer.write)
    conn.setopt(pycurl.INTERFACE, SECOND_IP)
    conn.perform()
    resp = buffer.getvalue()
    buffer.close()
    conn.close()
    RESPONSE_SECOND = resp

    # s = req.Session()
    # s.mount('http://', SourceAddressAdapter(SECOND_IP))
    # RESPONSE_SECOND = s.get(URL, headers=headers).content

    log.info("--- Secondary GET is done")


# Push back GET request responses to client
def pushBackToClient(self):
    global RESPONSE, RESPONSE_PRIMARY, RESPONSE_SECOND, REQUEST_HANDLE_TIME, START, END

    self.send_response(206)
    self.send_header('Accept-Ranges', "bytes")
    self.send_header('Content-Type', CONTENT_TYPE)
    self.send_header('Access-Control-Allow-Origin', '*')
    self.send_header('Content-Range',
                     "bytes " + str(PRIMARY_RANGE_START) + "-" + str(SECOND_RANGE_END) + "/" + str(CONTENT_LENGTH))
    self.send_header('Content-Length', str(SEGMENT_SIZE))
    try:
        self.end_headers()
        self.wfile.write(RESPONSE)
        log.info("Response is pushed back to client")
        REQUEST_HANDLE_TIME = getCurrentTime()
        log.info("Total time passed: %s seconds", str(round(REQUEST_HANDLE_TIME - REQUEST_RECV_TIME, 2)))
    except:
        log.error("**************** Connection aborted ******************")
    RESPONSE_PRIMARY = b""
    RESPONSE_SECOND = b""
    RESPONSE = b""
    START = ''
    END = ''


def getCurrentTime():
    return datetime.now(timezone.utc).timestamp()


def convertToMb(num):
    return num / (1024 * 1024)


class Proxy(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        global REQUEST_RECV_TIME
        if self.path.startswith("/http"):
            print("--- got new -----")
            log.info("--------------------------Gateway got a new request-------------------------------")
            REQUEST_RECV_TIME = getCurrentTime()
            handleRequest(self)
            print("--- done -----")
            log.info("---------------------------- DONE -----------------------------------------\n")
        else:
            log.error("Undefined format")


addrs = psutil.net_if_addrs()
print(addrs.keys())
log.basicConfig(filename='D:\\PyCharm Projects\\Senior\\src\\log_records\\gateway_v3.log', level=log.DEBUG,
                format='%(asctime)s - %(message)s')
connection = ThreadingHTTPServer((GATEWAY_IP, GATEWAY_PORT), Proxy)
connection.serve_forever()
