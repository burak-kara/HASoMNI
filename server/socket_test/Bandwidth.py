import time
import psutil

old_value = 0


def convert_to_gbit(value):
    return value / 1024. / 1024. / 1024. * 8


def send_stat(value):
    print(convert_to_gbit(value))


while True:
    new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
    if old_value:
        send_stat(new_value - old_value)

    old_value = new_value

    time.sleep(1)
