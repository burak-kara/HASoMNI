import os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime

LOCAL_PATH = '/src/server/static_files'
SERVER_PATH = '/home/ec2-user/server/'
PATH = SERVER_PATH
PORT = 8080

LOCAL_ADDRESS = '192.168.1.34'
OZU_ADDRESS = '10.200.106.78'
SERVER_ADDRESS = '172.31.39.64'
ADDRESS = SERVER_ADDRESS


def createBody(self, code=200, contentRange=""):
    file = open(getFilePath(self.path), 'rb')
    if code == 206:
        ranges = getBeginEnd(contentRange)
        file.seek(ranges[0], 0)
        self.wfile.write(file.read(ranges[1] - ranges[0]))
    else:
        self.wfile.write(file.read())
    file.close()


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


def getTime():
    now = datetime.now()
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)


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


class HTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        isRange = isRangeRequest(self.headers)
        if not isRange[0]:
            createHeaders(self)
            createBody(self)
        else:
            createHeaders(self, 206, isRange[1])
            createBody(self, 206, isRange[1])

    def do_HEAD(self):
        createHeaders(self)


print("---- Server started. Waiting for incoming requests ----")
httpWifi = ThreadingHTTPServer((ADDRESS, PORT), HTTPRequestHandler)
httpWifi.serve_forever()
