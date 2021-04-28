import sys
import json
from datetime import datetime
import os
import subprocess
import time
from dateutil import tz
import pandas as pd
import numpy as np

sys.path.insert(1, "/home/pi/trading/python_trading/Src")
from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse
from driver import Driver
import math


# res = ["a", "b"]
# print("hai " + sys.argv[1] + json.dumps(res))
# LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
# previousMonth = datetime.now().month - 1 or 12
# subprocess.call(
#     "{0}/logs/deleteLogs.sh {1}".format(
#         LOCATE_PY_DIRECTORY_PATH,
#         previousMonth if previousMonth / 10 > 1 else "0" + str(previousMonth),
#     ),
#     shell=True,
# )
# d = {"sad": "asdf", "dad": "asdf"}
# print(list(d.keys()))
nse = Nse()
stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
finaldf = pd.DataFrame()
dflist = []
dict = {}

dri = Driver()


# to get the months's record of all stocks with close price to calculate Efficient frontier
# for ticker in stocks_of_sector["symbol"]:
#     ticker_data = yf(ticker, result_range="1mo", interval="1d").result
#     dict = {
#         "date": [
#             time.strftime("%d-%m-%Y", time.localtime(x / 1000000000))
#             for x in ticker_data.index.values.tolist()
#         ],
#         ticker.split(".")[0]: ticker_data["Close"].tolist(),
#     }
#     dflist.append(pd.DataFrame(dict))

# finaldf = pd.concat(
#     (df.set_index("date") for df in dflist), axis=1, join="inner"
# ).reset_index()
# print(finaldf)
# finaldf.to_csv("data.csv")

# GET THE DAYS RESULT P/L

portfolio = pd.DataFrame(
    columns=["stock", "trade", "boughtAt", "soldAt", "quantity", "P/L"]
)
dri.run_strategy(sec="FO Stocks", strategy=dri.days_high_low)
day_high_low = dri.day_high_dict
stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
for stock in stocks_of_sector["symbol"]:

    print(f"checking {stock}")
    ticker_data = dri.get_ticker_data(ticker=stock, interval="5m")
    # print(ticker_data.tail(7))
    # exit()
    buy_value = ticker_data[ticker_data["Close"] > ticker_data.head(9)["High"].max()].head(1)
    sell_value = ticker_data[ticker_data["Close"] < ticker_data.head(9)["Low"].min()].head(1)
    if not buy_value.empty:
        t = buy_value.index.values[0]
        buy_value = buy_value.iloc[0]["Close"]
        if buy_value <= 5000 and t < np.datetime64("2021-04-27 15:00:00"):
            df = {
                "stock": stock,
                "trade": "buy",
                "time": t,
                "boughtAt": buy_value,
                "soldAt": ticker_data.iloc[-7]["Close"],
                "quantity": math.floor(5000 / buy_value),
                "P/L": (ticker_data.iloc[-7]["Close"] - buy_value)
                * math.floor(5000 / buy_value),
            }
            portfolio = portfolio.append(df, ignore_index=True)
    elif not sell_value.empty:
        t = sell_value.index.values[0]
        sell_value = sell_value.iloc[0]["Close"]
        if sell_value <= 5000 and t < np.datetime64("2021-04-27 15:00:00"):
            df = {
                "stock": stock,
                "trade": "sell",
                "time": t,
                "boughtAt": ticker_data.iloc[-7]["Close"],
                "soldAt": sell_value,
                "quantity": math.floor(5000 / sell_value),
                "P/L": (sell_value - ticker_data.iloc[-7]["Close"])
                * math.floor(5000 / sell_value),
            }
            portfolio = portfolio.append(df, ignore_index=True)
    else:
        print(f"this stock {stock} is in sideways, hence not added to portfolio")
    portfolio.set_index("stock")

print("*******PORTFOLIO*********")
print(portfolio)
# portfolio.to_csv("daysPL.csv")
print("today's outcome:{}".format(portfolio["P/L"].sum()))
