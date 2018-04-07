
import csv, json, sys
from datetime import datetime, timedelta

class OrderbookSimulator:
    file = None
    order_data = None
    bids = None
    asks = None
    current_date_time = None

    def __init__(self):
        pass

    def load(self, filename):
        with open(filename) as f:
            csv_reader = csv.reader(f)
            self.order_data = [[l[0], json.loads(l[1])] for l in csv_reader]

            while len(self.order_data) > 0:
                line = self.order_data.pop(0)
                #json_data = json.loads(line[1])
                if "method" in line[1] and line[1]["method"] == "snapshotOrderbook":
                    self.__load_order_book(line[1]["params"], line[0])
                    break

    def tick(self):
        tick_to = self.current_date_time + timedelta(seconds=1)
        #print "From " + str(self.current_date_time) + " to " + str(tick_to)

        while len(self.order_data) > 0 and self.__parse_datetime(self.order_data[0][0]) < tick_to:
            line = self.order_data.pop(0)
            if "method" in line[1]:
                if line[1]["method"] == "snapshotOrderbook":
                    self.__load_order_book(line[1]["params"], line[0])

                if line[1]["method"] == "updateOrderbook":
                    #print "updateOrderbook"
                    self.asks = self.__apply_update(self.asks, line[1]["params"]["ask"])
                    self.bids = self.__apply_update(self.bids, line[1]["params"]["bid"], True)
        self.current_date_time = tick_to

    def __load_order_book(self, orderbook, ob_datetime):
        self.current_date_time = self.__parse_datetime(ob_datetime)
        self.bids = orderbook["bid"]
        self.asks = orderbook["ask"]

    def __parse_datetime(self, str_date_time):
        return datetime.strptime(str_date_time.split(".")[0], "%Y-%m-%d %H:%M:%S")

    def __apply_update(self, original_list, update, reverse_list=False):
        #Remove everything from the order book that is in the update
        update_prices = [a["price"] for a in update]
        original_list = [a for a in original_list if a["price"] not in update_prices]

        #Add in the new orders
        original_list.extend([u for u in update if float(u["size"]) <> 0.0])

        #Sort by price
        original_list = sorted(original_list, key=lambda u: float(u["price"]), reverse=reverse_list)

        return original_list


if __name__ == "__main__":
    o = OrderbookSimulator()
    o.load(sys.argv[1])
    #print o.asks
    end_time = o.current_date_time + timedelta(hours=60)
    while o.current_date_time < end_time and len(o.order_data) > 0:
        o.tick()
        bbp = float(o.bids[0]["price"])
        bbs = float(o.bids[0]["size"])
        bap = float(o.asks[0]["price"])
        bas = float(o.asks[0]["size"])
        fv2 = (bbp*bas + bap*bbs)/(bas+bbs)
        print "%s,%s,%s,%f,%f" % (str(o.current_date_time), o.bids[0]["price"], o.asks[0]["price"], float(o.bids[0]["price"]) + ((float(o.asks[0]["price"]) - float(o.bids[0]["price"])) / 2), fv2)
    #print o.asks
