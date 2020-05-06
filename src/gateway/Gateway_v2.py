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
PRIMARY_RANGE_END = 0
SECOND_RANGE_START = 0
SECOND_LOAD = 0

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


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        global REQUEST_RECV_TIME
        if self.path.startswith("/http"):
            log.info("Gateway got a new request")
            # REQUEST_RECV_TIME = getCurrentTime()
            # handleRequest(self)
            log.info("---------------------------------------------------------------------\n")
        else:
            log.error("Undefined format")


log.basicConfig(filename='/log_records/gateway_v2.log', level=log.DEBUG, format='%(asctime)s - %(message)s')
connection = ThreadingHTTPServer((GATEWAY_IP, GATEWAY_PORT), Proxy)
connection.serve_forever()
