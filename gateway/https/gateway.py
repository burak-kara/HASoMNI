from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.path)


server_address = ('127.0.0.1', 4443)
httpd = HTTPServer(server_address, Proxy)
httpd.socket = ssl.wrap_socket(httpd.socket,
                               server_side=True,
                               certfile='D:\\PyCharm Projects\\Senior\\gateway\\https\\server.pem',
                               ssl_version=ssl.PROTOCOL_TLSv1)
httpd.serve_forever()
