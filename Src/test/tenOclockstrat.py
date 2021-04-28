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

nse = Nse()
stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
finaldf = pd.DataFrame()
dflist = []
dict = {}
dri = Driver()
portfolio = pd.DataFrame(
    columns=["stock", "trade", "boughtAt", "soldAt", "quantity", "P/L"]
)

# GET THE DAYS RESULT P/L


def update_portfolio(stock):
    global portfolio
    print(f"checking {stock}")
    month_ticker_data = dri.get_ticker_data(ticker=stock, range="15d", interval="5m")
    list_of_td = [
        month_ticker_data.iloc[i : i + 75, :]
        for i in range(0, len(month_ticker_data), 75)
    ]
    for ticker_data in list_of_td:
        buy_value = ticker_data[
            ticker_data["Close"] > ticker_data.head(9)["High"].max()
        ].head(1)
        sell_value = ticker_data[
            ticker_data["Close"] < ticker_data.head(9)["Low"].min()
        ].head(1)
        if not buy_value.empty:
            t = buy_value.index.values[0]
            buy_value = buy_value.iloc[0]["Close"]
            if buy_value <= 5000 and t < np.datetime64(
                "{} 15:00:00".format(pd.to_datetime(t).strftime("%Y-%m-%d"))
            ):
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
            if sell_value <= 5000 and t < np.datetime64(
                "{} 15:00:00".format(pd.to_datetime(t).strftime("%Y-%m-%d"))
            ):
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
            print(
                f"On {ticker_data.index.values[0]} this stock {stock} is in sideways, hence not added to portfolio"
            )


dri.run_strategy(sec="FO Stocks", strategy=dri.days_high_low)
day_high_low = dri.day_high_dict
stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
for stock in stocks_of_sector["symbol"][:1]:
    update_portfolio(stock)

portfolio = portfolio.set_index("stock")
print("*******PORTFOLIO*********")
print(portfolio)
# portfolio.to_csv("28-4-21.csv")
print("today's outcome:{}".format(portfolio["P/L"].sum()))
