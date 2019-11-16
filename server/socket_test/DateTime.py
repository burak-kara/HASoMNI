from datetime import datetime, timezone
import time

print(datetime.now(timezone.utc).strftime("%d %m %Y %H:%M:%S"))

millis = int(round(time.time() * 1000))
print(millis)

# current date and time
now = datetime.now(timezone.utc)
print(now)
timestamp = datetime.timestamp(now)
print("timestamp =", timestamp)
print("-------------------------")
print(round(time.time()))
