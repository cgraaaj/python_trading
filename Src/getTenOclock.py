import os
import json
import concurrent.futures
import telegram
import time
import sys
import pandas as pd
import math
from dotenv import load_dotenv
import datetime as dt
import logging

from driver import Driver
from datetime import datetime
from pprint import pprint
import time

start_time = time.time()
LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
load_dotenv("{}/.env".format(LOCATE_PY_DIRECTORY_PATH))

log_formatter = logging.Formatter(
    "%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    "%m-%d %H:%M:%S",
)


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(log_formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


logger = setup_logger(
    "default",
    "{}/logs_tele/".format(LOCATE_PY_DIRECTORY_PATH)
    + dt.datetime.now().strftime("%d-%m-%Y")
    + "_portfolio.log",
)

dri = Driver()
res = {}
toSend = []
dfFinal = pd.DataFrame()
oldStocksBuy = []
oldStocksSell = []
stocks = {}
capital = 100000
portfolio = pd.DataFrame(columns=["stock", "boughtAt", "soldAt", "quantity", "P_L"])
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
    global portfolio
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
        if "day_high" in df.columns:
            dfBuy = pd.DataFrame(df[df["day_high"].notnull()])
            toSendB = list(set(dfBuy.index.values.tolist()) - set(oldStocksBuy))
            dfBuy = dfBuy[dfBuy.index.isin(toSendB)]
            if toSendB:
                oldStocksBuy = oldStocksBuy + toSendB
        if "day_low" in df.columns:
            dfSell = pd.DataFrame(df[df["day_low"].notnull()])
            toSendS = list(set(dfSell.index.values.tolist()) - set(oldStocksSell))
            dfSell = dfSell[dfSell.index.isin(toSendS)]
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
        for index, row in dfFinal.iterrows():
            if row["brk_val"] <= 5000:
                if "Buy" in row["trade"]:
                    df = {
                        "stock": index,
                        "boughtAt": row["brk_val"],
                        "soldAt": 0,
                        "quantity": math.floor(5000 / row["brk_val"]),
                        "P_L": 0,
                    }
                else:
                    df = {
                        "stock": index,
                        "boughtAt": 0,
                        "soldAt": row["brk_val"],
                        "quantity": math.floor(5000 / row["brk_val"]),
                        "P_L": 0,
                    }
                portfolio = portfolio.append(df, ignore_index=True)
        print("*******PORTFOLIO*********")
        print(portfolio)
        logger.info(portfolio)
        portfolio.to_csv("days_PL.csv")
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
t_end = time.time() + (60 * ((5 * 60) + 15))
sqr_off_time = time.time() + (60 * (5 * 60))
# sqr_off_time = time.time() + (60 * (5 * 60))
while time.time() < t_end:
    print(
        "the current time is {} and the end time is {}".format(
            time.strftime("%H:%M:%S", time.localtime(time.time())),
            time.strftime("%H:%M:%S", time.localtime(t_end)),
        )
    )
    getStocks(trade)
    if time.time() > sqr_off_time:
        portfolio.set_index("stock", inplace=True)
        print("*********SQUARING OFF***********")
        logger.info("*********SQUARING OFF***********")
        for index, row in portfolio.iterrows():
            closeVal = dri.get_ticker_data(
                interval="1d", range="5m", ticker=index + ".NS"
            ).iloc[-2]["Close"]
            if row["soldAt"] == 0:
                portfolio.at[index, "soldAt"] = closeVal
                portfolio.at[index, "P_L"] = (closeVal - row["boughtAt"]) * row[
                    "quantity"
                ]
            else:
                portfolio.at[index, "boughtAt"] = closeVal
                portfolio.at[index, "P_L"] = (row["soldAt"] - closeVal) * row[
                    "quantity"
                ]
        print(portfolio)
        logger.info(portfolio)
        print("today's outcome:{}".format(portfolio["P_L"].sum()))
        logger.info("today's outcome:{}".format(portfolio["P_L"].sum()))
        exit()
    time.sleep(300.0 - (time.time() - start_time) % 300.0)