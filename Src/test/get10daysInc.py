import sys
import json
from datetime import datetime
import os
import subprocess
import time
from dateutil import tz
import multiprocessing
import pandas as pd
import numpy as np
import concurrent.futures

sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")
from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse
from driver import Driver
import math

nse = Nse()
# stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
# stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
# finaldf = pd.DataFrame()
# dflist = []
# dict = {}
dri = Driver()
res =  multiprocessing.Manager().list()

def get_uptrend(stock):
    # print(f"checking {stock}")
    rnge = 5
    ticker_data = dri.get_ticker_data(ticker=stock, range=str(rnge) + "d", interval="1d")
    # ticker_data = yf(stock,start="2021-06-21",end="2021-06-23", interval="1d").result
    ticker_data["uptrendClose"] = ticker_data["Close"] > ticker_data["Close"].shift(1)
    # print(ticker_data)
    # false
    # print((~ticker_data["uptrend"]).values.sum())
    # evaluates with 70% of actual days
    # print(ticker_data)
    # print(ticker_data["uptrend"].values.sum())
    # print(ticker_data.shape[0] * 0.70)
    # if ticker_data["uptrend"].values.sum() >= ticker_data.shape[0] * 0.70:
    # evaluates with range
    if ticker_data["uptrendClose"].values.sum() == rnge-1:
        print(ticker_data)
        print(stock)
        res.append(stock)

def get_flat(stock):
    rnge = 15
    ticker_data = dri.get_ticker_data(ticker=stock, range=str(rnge) + "d", interval="1d")
    ticker_data["isFlat"] = (
        (ticker_data["Close"] <= ticker_data.iloc[0]["Close"])
        & (
            ticker_data["Close"]
            > (ticker_data.iloc[0]["Close"] - (ticker_data.iloc[0]["Close"] * 0.02))
        )
        & (
            ticker_data["Close"]
            < (ticker_data.iloc[0]["Close"] + (ticker_data.iloc[0]["Close"] * 0.02))
        )
    )
    if ticker_data["isFlat"].values.sum() >= ticker_data.shape[0] * 0.80:
        print(ticker_data)
        res.append(stock)

sectors = pd.read_csv("/home/pudge/Trading/python_trading/Src/nsetools/sectorKeywords.csv")

# sectors = ["FO Stocks"]
for sec in sectors["Sector"].tail(3):
# for sec in sectors:
    print(sec)
    stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector=sec))
    stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        executor.map(get_uptrend, stocks_of_sector["symbol"])
    # for stock in stocks_of_sector["symbol"]:
    #     get_uptrend(stock)
        # get_flat(stock)

print(f"final result {list(set(res))}")
# update_portfolio("JSWSTEEL.NS")
# get_flat("MARUTI.NS")

# get_uptrend("GODREJAGRO.NS")