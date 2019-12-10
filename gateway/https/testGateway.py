from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import ssl
import http.client as hc


def do_HTTPS_connection(self):
    con = hc.HTTPSConnection('www.youtube.com')
    con.request("GET", "/")
    response = con.getresponse()
    con.close()
    try:
        RESPONSE = response.read()
    except hc.IncompleteRead as e:
        RESPONSE = e.partial
    self.send_response(200)
    self.send_header('Access-Control-Allow-Origin', '*')
    self.end_headers()
    print(RESPONSE)
    self.wfile.write(RESPONSE)


class Proxy(SimpleHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        do_HTTPS_connection(self)


server_address = ('192.168.1.34', 4443)
httpd = ThreadingHTTPServer(server_address, Proxy)
httpd.socket = ssl.wrap_socket(httpd.socket,
                               server_side=True,
                               certfile='D:\\PyCharm Projects\\Senior\\gateway\\https\\server.pem',
                               ssl_version=ssl.PROTOCOL_TLSv1_2)
print("serving....")
httpd.serve_forever()
