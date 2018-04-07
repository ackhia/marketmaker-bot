
import csv
import json
import sys

class CsvDatasource:
    def __init__(self, filename):
        self.filename = filename

    def subscribe(self, callback):
        with open(self.filename) as f:
            csv.field_size_limit(sys.maxsize)
            csv_reader = csv.reader(f)
            for l in csv_reader:
                if len(l) == 2:
                    callback([l[0], json.loads(l[1])])
                else:
                    print("Error in line: " + str(l))


if __name__ == "__main__":
    d = CsvDatasource("../data/btcusd.csv")

    def print_callback(x):
        print(x)

    d.subscribe(print_callback)