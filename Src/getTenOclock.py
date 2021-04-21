import os
import json
import concurrent.futures
import telegram
import time
import sys

from driver import Driver
from datetime import datetime
from pprint import pprint
import time

start_time = time.time()
LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))

dri = Driver()
res = {}
toSend = []
oldStocks = []
stocks = {}
bot = telegram.Bot(token="1667958437:AAHD9dnq51iuNeZDPa9gDhtJSCSTza4thto")


def send_stocks(id):
    bot.sendMessage(chat_id=id, text="Alert, These stocks broke days high...")
    for stock in toSend:
        bot.sendMessage(
            chat_id=id,
            text="{} has broke {} with {}".format(
                stock, stocks[stock]["day_high"], stocks[stock]["crnt_val"]
            ),
        )


def getStocks(trade):
    global toSend
    global stocks
    global oldStocks
    if trade == "equity":
        dri.run_strategy(sec="FO Stocks", strategy=dri.days_high_break)
    elif trade == "bitcoin":
        dri.run_strategy(
            sec=marketcap_BTCs_USD.split(","), strategy=dri.days_high_break
        )
    res["time"] = datetime.now().strftime("%H:%M:%S")
    try:
        res["stocks"] = list(dri.get_result()[0]["stocks"])
        dri.set_result()
        for x in res["stocks"]:
            stocks.update(x)
        res["stocks"] = list(stocks.keys())
        toSend = list(set(res["stocks"]) - set(oldStocks))
        file1 = open("{}/data/chat_ids.txt".format(LOCATE_PY_DIRECTORY_PATH), "r")
        chat_ids = file1.readlines()
        # processes = []
        # for id in chat_ids:
        #     p = multiprocessing.Process(target=send_stocks, args=[id, res["stocks"]])
        #     p.start()
        #     processes.append(p)
        # for pros in processes:
        #     pros.join()
        if len(toSend) > 0:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                executor.map(send_stocks, chat_ids)
            # results = [executor.submit(send_stocks, id, res["stocks"]) for id in chat_ids]
            # to get results of that function
            # for f in concurrent.futures.as_completed(results):
            #     print(f.result())

            with open("/home/pi/telegramBOT/stock_bot/data/data.json", "a") as outfile:
                outfile.write("\n")
                json.dump(toSend, outfile)
        if toSend:
            oldStocks = oldStocks + toSend
        print("--- %s seconds ---" % (time.time() - start_time))
    except:
        print("no stock has broke day's high")


# dri.run_strategy(sec="FO Stocks", strategy=dri.days_high)
# time.sleep(10)
# getStocks()
marketcap_BTCs_INR = "BTC-INR,ETH-INR,BNB-INR,XRP-INR,USDT-INR,ADA-INR,DOGE-INR,DOT1-INR,UNI3-INR,LTC-INR,LINK-INR,BCH-INR,THETA-INR,XLM-INR,FIL-INR,USDC-INR,VET-INR,TRX-INR,EOS-INR,SOL1-INR,BSV-INR,MIOTA-INR,LUNA1-INR,CRO-INR"
marketcap_BTCs_USD = "BTC-USD,ETH-USD,BNB-USD,XRP-USD,USDT-USD,ADA-USD,DOT1-USD,DOGE-USD,LTC-USD,BCH-USD,UNI3-USD,LINK-USD,VET-USD,XLM-USD,THETA-USD,FIL-USD,TRX-USD,USDC-USD,BSV-USD,EOS-USD,SOL1-USD,MIOTA-USD,NEO-USD,BTT1-USD"
trade = sys.argv[1]
if trade == "equity":
    dri.run_strategy(sec="FO Stocks", strategy=dri.days_high)
elif trade == "bitcoin":
    dri.run_strategy(sec=marketcap_BTCs_USD.split(","), strategy=dri.days_high)
else:
    print("Give some arguments like equity or bitcoin")

# time.sleep(60 * 4)
time.sleep(10)
# from 10:15 to 3:30
t_end = time.time() + 60 * ((5 * 60) + 15)
while time.time() < t_end:
    getStocks(trade)
    time.sleep(300.0 - (time.time() - start_time) % 300.0)