import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import datetime, timezone

LOCAL_PATH = '/src/server/static_files'
SERVER_PATH = '/home/ec2-user/server/'
PATH = SERVER_PATH
PORT = 8080

LOCAL_ADDRESS = '192.168.1.34'
OZU_ADDRESS = '10.200.106.78'
SERVER_ADDRESS = '172.31.39.64'
ADDRESS = SERVER_ADDRESS


def getCurrentTime():
    return datetime.now(timezone.utc).timestamp()


def createBody(self, code=200, contentRange=""):
    file = open(getFilePath(self.path), 'rb')
    print("I opened the file and started to serve it")
    if code == 206:
        ranges = getBeginEnd(contentRange)
        print("Ranges: " + str(ranges[0]) + " and " + str(ranges[1]))
        file.seek(ranges[0], 0)
        self.wfile.write(file.read(ranges[1] - ranges[0] + 1))
    else:
        self.wfile.write(file.read())
    file.close()
    print("I closed the file and my file service is done")


def getBeginEnd(contentRange):
    begin = int(contentRange.split("-")[0])
    end = int(contentRange.split("-")[1])
    return begin, end


def addRangeHeaders(self, contentRange, size):
    ranges = getBeginEnd(contentRange)
    contentRage = "bytes " + str(ranges[0]) + "-" + str(ranges[1]) + "/" + str(size)
    self.send_header("Content-Range", contentRage)


def getFileSize(path):
    return os.path.getsize(path)


def getFileType(path):
    if path.endswith('.html'):
        return 'text/html'
    elif path.endswith('.txt'):
        return 'text/plain'
    elif path.endswith('.mp4'):
        return 'video/mp4'
    else:
        return 'text/plain'


def getFilePath(path):
    if path == '/test20mb' or path == '/test150mb':
        return PATH + path[1:]
    elif path == '/testVideo':
        return PATH + path[1:] + '.mp4'
    else:
        return PATH + 'index.html'


def getHeaderValues(path):
    file = getFilePath(path)
    fileType = getFileType(file)
    size = getFileSize(file)
    return fileType, size, file


def createHeaders(self, code=200, contentRange=""):
    headerValues = getHeaderValues(self.path)
    self.send_response(code)
    self.send_header('Accept-Ranges', 'bytes')
    self.send_header('Content-type', headerValues[0])
    self.send_header('Content-Length', headerValues[1])
    if code == 206:
        addRangeHeaders(self, contentRange, headerValues[1])
    self.end_headers()


def isRangeRequest(headers):
    headerDict = dict(zip(headers.keys(), headers.values()))
    if "Range" not in headerDict.keys():
        return False, ""
    else:
        return True, headerDict["Range"].split("=")[1]


class Server(SimpleHTTPRequestHandler):
    def do_GET(self):
        print("I got a new request. my time is: " + str(getCurrentTime()))
        isRange = isRangeRequest(self.headers)
        if not isRange[0]:
            createHeaders(self)
            createBody(self)
        else:
            createHeaders(self, 206, isRange[1])
            createBody(self, 206, isRange[1])
        print("I handled the request. my time became: " + str(getCurrentTime()))

    def do_HEAD(self):
        print("I got HEAD request")
        createHeaders(self)


print("---- Server started. Waiting for incoming requests ----")
httpWifi = ThreadingHTTPServer((ADDRESS, PORT), Server)
httpWifi.serve_forever()
