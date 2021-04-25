import os
import json
import concurrent.futures
import telegram
import time
import sys
import pandas as pd
from dotenv import load_dotenv

from driver import Driver
from datetime import datetime
from pprint import pprint
import time

start_time = time.time()
LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
load_dotenv("{}/.env".format(LOCATE_PY_DIRECTORY_PATH))

dri = Driver()
res = {}
toSend = []
dfFinal = pd.DataFrame()
oldStocksBuy = []
oldStocksSell = []
stocks = {}
capital = 100000
bot = telegram.Bot(token=os.getenv("STOCK_BOT_TOKEN"))


def send_stocks(id):
    bot.sendMessage(chat_id=id, text="Alert, These stocks broke days high...")
    for index, row in dfFinal.iterrows():
        if pd.isnull(row["day_low"]):
            bot.sendMessage(
                chat_id=id,
                text="{} {}. It broke {} with {}".format(
                    row["trade"], index, row["day_high"], row["brk_val"]
                ),
            )
        else:
            bot.sendMessage(
                chat_id=id,
                text="{} {}. It broke {} with {}".format(
                    row["trade"], index, row["day_low"], row["brk_val"]
                ),
            )


def getStocks(trade):
    global oldStocksBuy
    global oldStocksSell
    global dfFinal
    if trade == "equity":
        dri.run_strategy(sec="FO Stocks", strategy=dri.get_todays_stock)
    elif trade == "bitcoin":
        dri.run_strategy(
            sec=marketcap_BTCs_INR.split(","), strategy=dri.get_todays_stock
        )
    res["time"] = datetime.now().strftime("%H:%M:%S")
    try:
        res["stocks"] = list(dri.result[0]["stocks"])
        df = pd.DataFrame(res["stocks"])
        df.set_index("stock", inplace=True)
        print(df)
        if "day_high" in df.columns:
            dfBuy = pd.DataFrame(df[df["day_high"].notnull()])
            toSendB = list(set(dfBuy.index.values.tolist()) - set(oldStocksBuy))
            print(toSendB)
            dfBuy = dfBuy[dfBuy.index.isin(toSendB)]
            print(dfBuy)
            if toSendB:
                oldStocksBuy = oldStocksBuy + toSendB
        if "day_low" in df.columns:
            dfSell = pd.DataFrame(df[df["day_low"].notnull()])
            toSendS = list(set(dfSell.index.values.tolist()) - set(oldStocksSell))
            print(toSendS)
            dfSell = dfSell[dfSell.index.isin(toSendS)]
            print(dfSell)
            if toSendS:
                oldStocksSell = oldStocksSell + toSendS

        dri.result = ""
        if "day_high" in df.columns and "day_low" not in df.columns:
            dfFinal = dfBuy
        elif "day_low" in df.columns and "day_high" not in df.columns:
            dfFinal = dfSell
        else:
            dfFinal = pd.concat([dfBuy, dfSell])
        print(dfFinal)

        file1 = open("{}/data/chat_ids.txt".format(LOCATE_PY_DIRECTORY_PATH), "r")
        chat_ids = file1.readlines()
        # processes = []
        # for id in chat_ids:
        #     p = multiprocessing.Process(target=send_stocks, args=[id, res["stocks"]])
        #     p.start()
        #     processes.append(p)
        # for pros in processes:
        #     pros.join()
        if len(dfFinal.index.values.tolist()) > 0:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                executor.map(send_stocks, chat_ids)
            # results = [executor.submit(send_stocks, id, res["stocks"]) for id in chat_ids]
            # to get results of that function
            # for f in concurrent.futures.as_completed(results):
            #     print(f.result())

            with open("/home/pi/telegramBOT/stock_bot/data/data.json", "a") as outfile:
                outfile.write("\n")
                json.dump(dfFinal.to_json(), outfile)
        print("--- %s seconds ---" % (time.time() - start_time))
    except Exception as e:
        print(e)


# dri.run_strategy(sec="FO Stocks", strategy=dri.days_high)
# time.sleep(10)
# getStocks()
marketcap_BTCs_INR = "BTC-INR,ETH-INR,BNB-INR,XRP-INR,USDT-INR,ADA-INR,DOGE-INR,DOT1-INR,UNI3-INR,LTC-INR,LINK-INR,BCH-INR,THETA-INR,XLM-INR,FIL-INR,USDC-INR,VET-INR,TRX-INR,EOS-INR,SOL1-INR,BSV-INR,MIOTA-INR,LUNA1-INR,CRO-INR"
marketcap_BTCs_USD = "BTC-USD,ETH-USD,BNB-USD,XRP-USD,USDT-USD,ADA-USD,DOT1-USD,DOGE-USD,LTC-USD,BCH-USD,UNI3-USD,LINK-USD,VET-USD,XLM-USD,THETA-USD,FIL-USD,TRX-USD,USDC-USD,BSV-USD,EOS-USD,SOL1-USD,MIOTA-USD,NEO-USD,BTT1-USD"
trade = sys.argv[1]
if trade == "equity":
    dri.run_strategy(sec="FO Stocks", strategy=dri.days_high_low)
elif trade == "bitcoin":
    dri.run_strategy(sec=marketcap_BTCs_INR.split(","), strategy=dri.days_high_low)
else:
    print("Give some arguments like equity or bitcoin")

# time.sleep(60 * 4)
time.sleep(10)
# from 10:15 to 3:30
t_end = time.time() + 60 * ((7 * 60) + 15)
while time.time() < t_end:
    getStocks(trade)
    time.sleep(300.0 - (time.time() - start_time) % 300.0)