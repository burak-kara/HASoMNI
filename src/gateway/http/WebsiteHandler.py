from datetime import datetime, timezone
from wsgiref.handlers import format_date_time
import requests as req
from time import mktime
from socket import *
import threading

WIFI_IP = '192.168.1.34'
MOBILE_IP = '192.168.43.38'
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
DEFAULT_PORT = 8080
MOBILE_PORT = 8081

REQUESTED_HOSTNAME = ''
REQUESTED_PATH = ''

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

RESPONSE_DEFAULT_HEAD = None
RESPONSE_DEFAULT = b""
RESPONSE_MOBILE = b""
RESPONSE = b""

LINE = "\r\n"
HEADER = LINE + LINE
HTTP_VERSION = "http://"


class WebsiteHttpHandler:
    def __init__(self, httpServerSelf):
        self.assignRequestedPath(httpServerSelf.path[1:])
        self.measureBandWidth()
        self.assignContentInfo()
        self.calculateLoadWeight()
        self.sendRangeRequest()
        self.pushBackToClient(httpServerSelf)

    # Assign requested ip, port and file path to global variables
    # Requested string comes in format of http://site/path
    @staticmethod
    def assignRequestedPath(requested):
        global REQUESTED_HOSTNAME, REQUESTED_PATH, HTTP_VERSION
        HTTP_VERSION = requested.split(":")[0] + "://"
        REQUESTED_HOSTNAME = requested.split("//")[1].split("/")[0]
        try:
            REQUESTED_PATH = requested.split("//")[1].split("/", 1)[1]
        except:
            print("no path found")

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
        global startTimeDefault, serverTimeDefault, RESPONSE_DEFAULT_HEAD
        startTimeDefault = self.getNow()
        response = req.head(HTTP_VERSION + REQUESTED_HOSTNAME + "/" + REQUESTED_PATH)
        serverTimeDefault = self.getNow()
        RESPONSE_DEFAULT_HEAD = response

    # return current time as timestamp
    @staticmethod
    def getNow():
        return datetime.now(timezone.utc).timestamp()

    # TODO modify like https/httpsSocket.py
    # Send HEAD request over second connection
    def sendHeadMobile(self):
        global startTimeMobile, serverTimeMobile, isSecondConnectionAvailable
        try:
            con = socket(AF_INET, SOCK_STREAM)
            con.bind((MOBILE_IP, MOBILE_PORT))
            con.connect((REQUESTED_HOSTNAME, 443))
            request = "HEAD / HTTP/1.1" + LINE
            request += "Connection: close" + HEADER
            startTimeMobile = self.getNow()
            con.sendall(request.encode('ascii'))
            con.recv(2048)
            serverTimeMobile = self.getNow()
            con.close()
        except Exception as exp:
            print(exp)
            print("second connection is not found")
            isSecondConnectionAvailable = False

    @staticmethod
    def assignContentInfo():
        global CONTENT_LENGTH, CONTENT_TYPE, isAcceptRanges
        try:
            if RESPONSE_DEFAULT_HEAD.headers["accept-ranges"].lower() == "none":
                isAcceptRanges = False
        except:
            print("accept ranges header was not found")
            isAcceptRanges = False
        try:
            CONTENT_LENGTH = int(RESPONSE_DEFAULT_HEAD.headers["content-length"])
        except:
            print("content length header was not found")
        try:
            CONTENT_TYPE = RESPONSE_DEFAULT_HEAD.headers["content-type"]
        except:
            print("content type header was not found")

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
        print(str(DEFAULT_RANGE_END) + "/" + str(CONTENT_LENGTH))
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
        RESPONSE_DEFAULT = req.get(HTTP_VERSION + REQUESTED_HOSTNAME + "/" + REQUESTED_PATH, headers=headers).content

    # TODO modify like https/httpsSocket.py
    @staticmethod
    def useMobile():
        global RESPONSE_MOBILE
        con = socket(AF_INET, SOCK_STREAM)
        con.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        con.bind((MOBILE_IP, MOBILE_PORT + 1))
        con.connect((REQUESTED_HOSTNAME, 443))
        request = "GET /" + REQUESTED_PATH + " HTTP/1.1" + LINE
        request += "Connection: close" + LINE
        request += "Range: bytes=" + str(MOBILE_RANGE_START) + "-" + str(CONTENT_LENGTH) + HEADER
        print(request)
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
