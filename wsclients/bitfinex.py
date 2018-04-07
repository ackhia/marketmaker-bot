
from websocket import create_connection
from json import loads

def subscribe_ticker(callback, pair):
    ws = create_connection("wss://api.bitfinex.com/ws/2")
    result = ws.recv()
    print result
    msg = '''{
      "event": "subscribe",
      "channel":"ticker",
      "pair":"%s"
    }''' % pair
    print "Sending: " + msg
    ws.send(msg)

    while True:
        result = ws.recv()
        result_json = loads(result)
        if type(result_json) is list and len(result_json) > 1 and type(result_json[1]) is list:
            callback({"bid": result_json[1][0], "ask": result_json[1][2]})
    ws.close()

def subscribe_ticker_depthchart(callback, pair):
    ws = create_connection("wss://api.bitfinex.com/ws/2")
    result = ws.recv()
    print result
    msg = '''{
      "event": "subscribe",
      "channel":"book",
      "pair":"%s",
      "prec":"P3"
    }''' % pair
    print "Sending: " + msg
    ws.send(msg)

    while True:
        result = ws.recv()
        result_json = loads(result)
        #if type(result_json) is list and len(result_json) > 1 and type(result_json[1]) is list:
            #callback({"bid": result_json[1][0], "ask": result_json[1][2]})
        callback(result_json)
    ws.close()



if __name__ == "__main__":
    def print_callback(x):
        print x

    subscribe_ticker_depthchart(print_callback, "BTCUSD")