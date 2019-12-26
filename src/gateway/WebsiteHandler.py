from datetime import datetime, timezone
from wsgiref.handlers import format_date_time
import requests as req
from time import mktime
from socket import *
import threading
import ssl
import config.config as cfg

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


class WebsiteHandler:
    def __init__(self, httpServerSelf):
        self.assignRequestedPath(httpServerSelf.path[1:])
        self.createSocketHeadHeaders()
        self.measureBandWidth()
        self.assignContentInfo()
        self.calculateLoadWeight()
        self.createSocketGetHeaders()
        self.sendRangeRequest()
        self.pushBackToClient(httpServerSelf)

    # Assign requested ip, port and file path to global variables
    # Requested string comes in format of http://site/path or https://site/path
    @staticmethod
    def assignRequestedPath(requested):
        global REQUESTED_HOSTNAME, REQUESTED_PATH, REQUESTED_PORT, HTTP_VERSION, IS_VERIFY
        HTTP_VERSION = requested.split(":")[0] + "://"
        print(HTTP_VERSION)  # TODO debug purpose
        if HTTP_VERSION.__contains__("s"):
            IS_VERIFY = True
            REQUESTED_PORT = cfg.requested['httpsPort']
        REQUESTED_HOSTNAME = requested.split("//")[1].split("/")[0]
        try:
            REQUESTED_PATH = '/' + requested.split("//")[1].split("/", 1)[1]
        except:
            print("no path found")

    @staticmethod
    def createSocketHeadHeaders():
        global SOCKET_HEAD_HEADERS
        SOCKET_HEAD_HEADERS = "HEAD " + REQUESTED_PATH + " HTTP/1.1" + LINE
        SOCKET_HEAD_HEADERS += "Host: " + REQUESTED_HOSTNAME + LINE
        SOCKET_HEAD_HEADERS += "Accept: */*" + LINE
        SOCKET_HEAD_HEADERS += "User-Agent: kibitzer" + LINE
        SOCKET_HEAD_HEADERS += "Connection: Close" + HEADER

    # Send two HEAD requests using threads
    def measureBandWidth(self):
        defaultThread = threading.Thread(target=self.sendHeadDefault)
        mobileThread = threading.Thread(target=self.sendHeadMobile)
        defaultThread.start()
        mobileThread.start()
        defaultThread.join()
        mobileThread.join()

    # Send HEAD request over default connection
    def sendHeadDefault(self):
        global START_STAMP_PRIMARY, END_STAMP_PRIMARY, HEAD_RESPONSE_HEADERS
        START_STAMP_PRIMARY = self.getNow()
        HEAD_RESPONSE_HEADERS = req.head(HTTP_VERSION + REQUESTED_HOSTNAME + REQUESTED_PATH, verify=IS_VERIFY).headers
        END_STAMP_PRIMARY = self.getNow()

    # return current time as timestamp
    @staticmethod
    def getNow():
        return datetime.now(timezone.utc).timestamp()

    # Send HEAD request over second connection
    def sendHeadMobile(self):
        global IS_SECOND_AVAILABLE
        try:
            con = socket(AF_INET, SOCK_STREAM)
            con.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            con.bind((SECOND_IP, SECOND_PORT))
            if IS_VERIFY:
                self.headHttpsSocket(con)
            else:
                self.headHttpSocket(con)
        except:
            print("second connection is not found")
            IS_SECOND_AVAILABLE = False

    def headHttpsSocket(self, con):
        global START_STAMP_SECOND, END_STAMP_SECOND
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_default_certs()
        ssl_socket = context.wrap_socket(con, server_hostname=REQUESTED_HOSTNAME)
        ssl_socket.connect((REQUESTED_HOSTNAME, REQUESTED_PORT))
        START_STAMP_SECOND = self.getNow()
        ssl_socket.sendall(SOCKET_HEAD_HEADERS.encode("utf-8"))
        ssl_socket.recv(1024)
        END_STAMP_SECOND = self.getNow()
        ssl_socket.close()
        con.close()

    def headHttpSocket(self, con):
        global START_STAMP_SECOND, END_STAMP_SECOND
        con.connect((REQUESTED_HOSTNAME, REQUESTED_PORT))
        START_STAMP_SECOND = self.getNow()
        con.sendall(SOCKET_HEAD_HEADERS.encode('utf-8'))
        con.recv(1024)
        END_STAMP_SECOND = self.getNow()
        con.close()

    @staticmethod
    def assignContentInfo():
        global CONTENT_LENGTH, CONTENT_TYPE, IS_ACCEPT_RANGE
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

    @staticmethod
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

    @staticmethod
    def createSocketGetHeaders():
        global SOCKET_GET_HEADERS
        SOCKET_GET_HEADERS = "GET " + REQUESTED_PATH + " HTTP/1.1" + LINE
        SOCKET_GET_HEADERS += "Host: " + REQUESTED_HOSTNAME + LINE
        SOCKET_GET_HEADERS += "Accept: */*" + LINE
        SOCKET_GET_HEADERS += "User-Agent: kibitzer" + LINE
        SOCKET_GET_HEADERS += "Range: bytes=" + str(SECOND_RANGE_START) + "-" + LINE
        SOCKET_GET_HEADERS += "Connection: Keep-Alive" + HEADER

    def sendRangeRequest(self):
        global RESPONSE
        defaultThread = threading.Thread(target=self.useDefault)
        if IS_SECOND_AVAILABLE and IS_ACCEPT_RANGE:
            mobileThread = threading.Thread(target=self.useMobile)
        defaultThread.start()
        if IS_SECOND_AVAILABLE and IS_ACCEPT_RANGE:
            mobileThread.start()
        defaultThread.join()
        if IS_SECOND_AVAILABLE and IS_ACCEPT_RANGE:
            mobileThread.join()
        RESPONSE = RESPONSE_PRIMARY + RESPONSE_SECOND

    @staticmethod
    def useDefault():
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

    def useMobile(self):
        global RESPONSE_SECOND
        con = socket(AF_INET, SOCK_STREAM)
        con.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        con.bind((SECOND_IP, SECOND_PORT + 1))
        if IS_VERIFY:
            self.getHttpsSocket(con)
        else:
            self.getHttpSocket(con)

    @staticmethod
    def getHttpsSocket(con):
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
        ssl_socket.close()
        con.close()

    @staticmethod
    def getHttpSocket(con):
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

    # TODO modify and add headers from range requests' responses
    @staticmethod
    def pushBackToClient(httpServerSelf):
        httpServerSelf.send_response(200)
        httpServerSelf.send_header('Content-Type', CONTENT_TYPE)
        httpServerSelf.send_header('Access-Control-Allow-Origin', '*')
        httpServerSelf.send_header('Content-Length', str(CONTENT_LENGTH))
        httpServerSelf.end_headers()
        httpServerSelf.wfile.write(RESPONSE)
