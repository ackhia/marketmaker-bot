

from wsclients import hitbtc
from datetime import datetime
import csv

def print_callback(x):
    print(x)


f = open("btcusd.csv", "w", newline='')
csv_writer = csv.writer(f)


def log_callback(x):
    csv_writer.writerow([datetime.now(), x.strip()])

hitbtc.subscribe_all(log_callback, 'BTCUSD')