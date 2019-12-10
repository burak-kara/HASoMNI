from datetime import datetime, timezone
from wsgiref.handlers import format_date_time
from time import mktime
import http.client as hc
from socket import *
import threading

WIFI_IP = '192.168.1.34'
MOBILE_IP = '172.20.10.13'
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
isSecondConnectionAvailable = True
isAcceptRanges = True

RESPONSE_DEFAULT_HEAD = None
RESPONSE_DEFAULT = b""
RESPONSE_MOBILE = b""
RESPONSE = b""

LINE = "\r\n"
HEADER = LINE + LINE


class WebsiteHttpHandler:
    def __init__(self, httpServerSelf):
        global REQUESTED_PATH
        REQUESTED_PATH = httpServerSelf.path[1:]
        pass

