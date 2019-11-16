from datetime import datetime, timezone
import time
from wsgiref.handlers import format_date_time
from time import mktime
import email.utils as eut

now = datetime.now()
stamp = mktime(now.timetuple())
print(format_date_time(stamp))  # --> Wed, 22 Oct 2008 10:52:40 GMT
t = format_date_time(stamp)

x = datetime(*eut.parsedate(t)[:6])
print(x)
# print(datetime.now(timezone.utc).strftime("%d %m %Y %H:%M:%S"))
#
# millis = int(round(time.time() * 1000))
# print(millis)
#
# # current date and time
# now = datetime.now(timezone.utc)
#
# timestamp = datetime.timestamp(now)
# print("timestamp =", timestamp)
# print("-------------------------")
# print(round(time.time()))
