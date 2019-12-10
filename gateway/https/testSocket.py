import socket
import ssl
import requests as req
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

WIFI_IP = '10.200.106.78'
MOBILE_IP = '172.20.10.13'
LAN_IP = '192.168.1.38'
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
DEFAULT_PORT = 8080
MOBILE_PORT = 8081

REQUESTED = ''


def doConnection(self):
    response = req.get(REQUESTED, verify=True)
    print(response.headers)
    self.send_response(response.status_code)
    self.send_header("Content-Type", response.headers["Content-Type"])
    self.end_headers()
    self.wfile.write(response.content)


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        global REQUESTED
        REQUESTED = self.path[1:]
        doConnection(self)


connection = ThreadingHTTPServer((DEFAULT_IP, DEFAULT_PORT), Proxy)
connection.serve_forever()
