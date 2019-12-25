from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from gateway.TestServerHandler import TestServerHandler
from gateway.WebsiteHandler import WebsiteHttpHandler
import config.config as cfg

GATEWAY_IP = cfg.primary['ip']
GATEWAY_PORT = cfg.primary['port']
TEST_SERVER_IP = cfg.server['ip']
TEST_SERVER_PORT = str(cfg.server['port'])


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/" + TEST_SERVER_IP + ":" + TEST_SERVER_PORT):
            TestServerHandler(self)
        elif self.path.startswith("/http"):
            WebsiteHttpHandler(self)
        else:
            # TODO implement error 404, 500 vs
            pass


connection = ThreadingHTTPServer((GATEWAY_IP, GATEWAY_PORT), Proxy)
connection.serve_forever()
