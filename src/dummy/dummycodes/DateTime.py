# from datetime import datetime, timezone, timedelta
# from wsgiref.handlers import format_date_time
# from time import mktime
# import email.utils as eut
#
# now = datetime.now()
# stamp = mktime(now.timetuple())
# print(stamp)
# print(format_date_time(stamp))  # --> Wed, 22 Oct 2008 10:52:40 GMT
# t = format_date_time(stamp)
#
#
# tt = datetime.now()
# print(tt.timestamp())  # 19:48:29.215217 // TODO use datetime.time
# # print(t)
# x = datetime(*eut.parsedate(t)[:6])
# print(x.timestamp())   # datetime.datetime
#
# delta = x.timestamp() - tt.timestamp()
# print(delta)
#
#
#
# # millis = int(round(time.time() * 1000))
# # print(time.time())
# #
# # current date and time
# # now = datetime.now(timezone.utc)
# # print(now)
# # print(now.hour, now.second)
# #
# # timestamp = datetime.timestamp(now)
# # print("timestamp =", timestamp)
# # print("-------------------------")
# # print(round(time.time()))
# #
# # print(datetime.now().isoformat(timespec='milliseconds'))


x = round(0.76443, 2)
print(x)