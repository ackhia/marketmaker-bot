
import os, thread
from datetime import datetime
from wsclients import hitbtc, bitfinex


hitbtc_bid, hitbtc_ask = 0, 0
bitfinex_bid, bitfinex_ask = 0, 0

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def render():
    global f
    cls()
    print "HitBTC: \tBid: %s\tAsk: %.8f\tSpread: %.8f" % (hitbtc_bid, hitbtc_ask, hitbtc_ask - hitbtc_bid)
    print "Bitfinex:\tBid: %s\tAsk: %.8f\tSpread: %.8f" % (bitfinex_bid, bitfinex_ask, bitfinex_ask - bitfinex_bid)
    print "Difference:\tBid: %.8f\tAsk: %.8f" % (bitfinex_bid - hitbtc_bid, bitfinex_ask - hitbtc_ask)
    f.write(str(datetime.now()) + ",")
    f.write("%.8f,%.8f,%.8f,%.8f\n" % (hitbtc_bid, hitbtc_ask,bitfinex_bid,bitfinex_ask))

def on_hitbtc(x):
    global hitbtc_bid, hitbtc_ask
    if hitbtc_bid != x["bid"] or hitbtc_ask != x["ask"]:
        hitbtc_bid = x["bid"]
        hitbtc_ask = x["ask"]
        render()

def on_bitfinex(x):
    global bitfinex_bid, bitfinex_ask
    if bitfinex_bid != x["bid"] or bitfinex_ask != x["ask"]:
        bitfinex_bid = x["bid"]
        bitfinex_ask = x["ask"]
        render()

f = open("price.csv", "a+")
thread.start_new_thread(hitbtc.subscribe_ticker, (on_hitbtc, "BTCUSD",))
thread.start_new_thread(bitfinex.subscribe_ticker, (on_bitfinex, "BTCUSD",))

raw_input()