from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from src.gateway.http.ServerHandler import ServerHandler
from src.gateway.http.WebsiteHandler import WebsiteHttpHandler

WIFI_IP = '10.200.106.78'
DEFAULT_IP = WIFI_IP
DEFAULT_PORT = 8080


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/3.134.95.115:8080"):
            ServerHandler(self)
        elif self.path.startswith("/http"):
            WebsiteHttpHandler(self)


connection = ThreadingHTTPServer((DEFAULT_IP, DEFAULT_PORT), Proxy)
connection.serve_forever()
