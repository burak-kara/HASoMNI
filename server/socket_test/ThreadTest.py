import threading
import time
from datetime import datetime, timezone
import http.client as hc


WIFI_IP = '192.168.1.34'
MOBILE_IP = '192.168.43.38'
LAN_IP = '192.168.1.38'
DEFAULT_IP = WIFI_IP
SECOND_IP = MOBILE_IP
PORT = 8080
REQUESTED_IP = '34.204.87.0'
REQUESTED_PORT = 8080
REQUESTED_FILE = '/'


def sendHeadDefault():
    con = hc.HTTPConnection(REQUESTED_IP, REQUESTED_PORT)
    startTime = datetime.now(timezone.utc)
    con.request("HEAD", "/" + REQUESTED_FILE, body=None)
    response = con.getresponse()
    endTime = datetime.now(timezone.utc)
    con.close()
    print(response.getheader("content-length"))
    print(startTime - endTime)


thread1 = threading.Thread(target=sendHeadDefault)
thread2 = threading.Thread(target=sendHeadDefault)
thread1.start()
thread2.start()

thread1.join()
thread2.join()
