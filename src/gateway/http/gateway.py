from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from src.gateway.http.ServerHandler import ServerHandler
from src.gateway.http.WebsiteHttpHandler import WebsiteHttpHandler
from src.gateway.http.WebsiteHttpsHandler import WebsiteHttpsHandler

WIFI_IP = '192.168.1.34'
DEFAULT_IP = WIFI_IP
DEFAULT_PORT = 8080


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/3.134.95.115:8080"):
            ServerHandler(self)
        elif self.path.startswith("/https"):
            # TODO call WebsiteHttpsHandler
            pass
        else:
            WebsiteHttpHandler(self)
            # TODO call WebsiteHttpHandler


connection = ThreadingHTTPServer((DEFAULT_IP, DEFAULT_PORT), Proxy)
connection.serve_forever()
