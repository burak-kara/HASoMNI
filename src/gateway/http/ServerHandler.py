from datetime import datetime, timezone
from wsgiref.handlers import format_date_time
from time import mktime
import http.client as hc
from socket import *
import threading
import config.config as cfg

WIFI_IP = cfg.wifi['ip']
MOBILE_IP = cfg.mobile['ip']
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
DEFAULT_PORT = cfg.wifi['port']
MOBILE_PORT = cfg.mobile['port']

REQUESTED_IP = ''
REQUESTED_PORT = 8080
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
isSecondConnectionAvailable = True
isAcceptRanges = True

HEAD_RESPONSE_HEADERS = None
RESPONSE_DEFAULT = b""
RESPONSE_MOBILE = b""
RESPONSE = b""

LINE = "\r\n"
HEADER = LINE + LINE


class ServerHandler:
    def __init__(self, httpServerSelf):
        self.assignRequestedPath(httpServerSelf.path[1:])
        self.measureBandWidth()
        self.assignContentInfo()
        self.calculateLoadWeight()
        self.sendRangeRequest()
        self.pushBackToClient(httpServerSelf)
        pass

    # Assign requested ip, port and file path to global variables
    @staticmethod
    def assignRequestedPath(requested):
        global REQUESTED_IP, REQUESTED_PORT, REQUESTED_FILE
        REQUESTED_IP = requested.split(":")[0]
        try:
            REQUESTED_PORT = int(requested.split(":")[1].split("/")[0])
        except:
            print("port not found")
        try:
            REQUESTED_FILE = requested.split("/")[1]
        except:
            print("requested file not found")

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
        global startTimeDefault, serverTimeDefault, HEAD_RESPONSE_HEADERS
        con = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
        startTimeDefault = self.getNow()
        con.request("HEAD", "/" + REQUESTED_FILE, body=None)
        response = con.getresponse()
        serverTimeDefault = self.getNow()
        con.close()
        RESPONSE_DEFAULT_HEAD = response

    # return current time as timestamp
    @staticmethod
    def getNow():
        return datetime.now(timezone.utc).timestamp()

    # Send HEAD request over second connection
    def sendHeadMobile(self):
        global startTimeMobile, serverTimeMobile, isSecondConnectionAvailable
        try:
            con = socket(AF_INET, SOCK_STREAM)
            con.bind((MOBILE_IP, MOBILE_PORT))
            con.connect((REQUESTED_IP, REQUESTED_PORT))
            request = "HEAD / HTTP/1.1" + LINE
            request += "Connection: close" + HEADER
            startTimeMobile = self.getNow()
            con.sendall(request.encode('ascii'))
            con.recv(2048)
            serverTimeMobile = self.getNow()
            con.close()
        except:
            print("second connection is not found")
            isSecondConnectionAvailable = False

    @staticmethod
    def assignContentInfo():
        global CONTENT_LENGTH, CONTENT_TYPE, isAcceptRanges
        if HEAD_RESPONSE_HEADERS.getheader("accept-ranges").lower() == "none":
            isAcceptRanges = False
        CONTENT_LENGTH = int(HEAD_RESPONSE_HEADERS.getheader("content-length"))
        CONTENT_TYPE = HEAD_RESPONSE_HEADERS.getheader("content-type")

    @staticmethod
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

    def sendRangeRequest(self):
        global RESPONSE
        defaultThread = threading.Thread(target=self.useDefault)
        if isSecondConnectionAvailable and isAcceptRanges:
            mobileThread = threading.Thread(target=self.useMobile)
        defaultThread.start()
        if isSecondConnectionAvailable and isAcceptRanges:
            mobileThread.start()
        defaultThread.join()
        if isSecondConnectionAvailable and isAcceptRanges:
            mobileThread.join()
        RESPONSE = RESPONSE_DEFAULT + RESPONSE_MOBILE

    @staticmethod
    def useDefault():
        global RESPONSE_DEFAULT
        if isAcceptRanges:
            rangeValue = 'bytes=0-' + str(DEFAULT_RANGE_END)
            headers = {'Connection': 'Keep-Alive', 'Range': rangeValue}
        else:
            headers = {'Connection': 'Keep-Alive'}
        con = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
        con.request("GET", "/" + REQUESTED_FILE, body=None, headers=headers)
        response = con.getresponse()
        con.close()
        try:
            RESPONSE_DEFAULT = response.read()
        except hc.IncompleteRead as e:
            RESPONSE_DEFAULT = e.partial

    @staticmethod
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

    def pushBackToClient(self, httpServerSelf):
        httpServerSelf.send_response(200)
        httpServerSelf.send_header('Content-type', CONTENT_TYPE)
        httpServerSelf.send_header('Access-Control-Allow-Origin', '*')
        httpServerSelf.send_header('Date', self.getTime())
        httpServerSelf.end_headers()
        httpServerSelf.wfile.write(RESPONSE)

    @staticmethod
    def getTime():
        now = datetime.now()
        stamp = mktime(now.timetuple())
        return format_date_time(stamp)
