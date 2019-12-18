from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from src.gateway.http.ServerHandler import ServerHandler
from src.gateway.http.WebsiteHandler import WebsiteHttpHandler
import config.config as cfg

WIFI_IP = cfg.wifi['ip']
DEFAULT_IP = WIFI_IP
DEFAULT_PORT = cfg.server['port']


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/"+cfg.server['ip']+":"+str(cfg.server['port'])):
            ServerHandler(self)
        elif self.path.startswith("/http"):
            WebsiteHttpHandler(self)
        else:
            # TODO implement error 404, 500 vs
            pass


connection = ThreadingHTTPServer((DEFAULT_IP, DEFAULT_PORT), Proxy)
connection.serve_forever()
