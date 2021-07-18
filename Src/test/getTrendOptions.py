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
import pandas_datareader as web
import concurrent.futures
import datetime as dt
import time
from pprint import pprint

sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")
from telegram_helper import Tele
from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse
from driver import Driver

# from sklearn.preprocessing import MinMaxScaler
import math

nse = Nse()
# stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
# stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
# finaldf = pd.DataFrame()
# dflist = []
# dict = {}
dri = Driver()
res = multiprocessing.Manager().list()
total = []
volBased = []
optionStocks = {"Bullish": [], "Bearish": []}


def get_uptrend(stock):
    # print(f"checking {stock}")
    total.append(stock)
    rnge = 15
    ticker_data = dri.get_ticker_data(
        ticker=stock, range=str(rnge) + "d", interval="1d"
    )
    ticker_data["uptrend"] = (ticker_data["Close"] > ticker_data["Close"].shift(1)) & (
        ticker_data["Close"] > ticker_data["Open"]
    )
    check_data(stock, ticker_data, rnge)
    if (
        ticker_data["uptrend"].values.sum() == ticker_data.shape[0] - 5
        and ticker_data.shape[0] == rnge
    ):
        # print(ticker_data)
        print(stock)
        res.append(stock)
        if ticker_data["Volume"].iloc[-1] > (ticker_data.iloc[:-1, -2].mean(axis=0)):
            volBased.append({"name": stock, "volume": ticker_data["Volume"].iloc[-1]})


def check_data(stock, ticker_data, rnge):
    if ticker_data.shape[0] != rnge:
        print(len(set(total)))
        time.sleep(120)
        print(f"checking again {stock}")
        get_uptrend(stock)


def get_flat(stock):
    rnge = 15
    ticker_data = dri.get_ticker_data(
        ticker=stock, range=str(rnge) + "d", interval="1d"
    )
    # start = dt.datetime.now() - dt.timedelta(days=rnge)
    # end = dt.datetime.now()
    # ticker_data = web.DataReader(stock, "yahoo", start, end)
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


def test_pandas_datareader():
    start = dt.datetime(2021, 6, 21)
    end = dt.datetime(2021, 6, 28)
    data = web.DataReader("CUB.NS", "yahoo", start, end)
    print(data)


def analyze_stock(data, stock):
    try:
        ce_data = data["filtered"]["CE"]
        pe_data = data["filtered"]["PE"]
        if ce_data["totOI"] > pe_data["totOI"]:
            print(f"{stock} bullish")
            optionStocks["Bullish"].append(
                {
                    "Name": stock,
                    "Percent": (ce_data["totOI"] / pe_data["totOI"]) * 100,
                    "PCR": (pe_data["totOI"] / ce_data["totOI"]),
                    "CE Volume": ce_data["totVol"],
                    "PE Volume": pe_data["totVol"],
                }
            )
        else:
            optionStocks["Bearish"].append(
                {
                    "Name": stock,
                    "Percent": (pe_data["totOI"] / ce_data["totOI"]) * 100,
                    "PCR": (pe_data["totOI"] / ce_data["totOI"]),
                    "CE Volume": ce_data["totVol"],
                    "PE Volume": pe_data["totVol"],
                }
            )
            print(f"{stock} bearish")
    except:
        print(data)
    # print(ce_data,pe_data)


sectors = pd.read_csv(
    "/home/pudge/Trading/python_trading/Src/nsetools/sectorKeywords.csv"
)
sectors = ["FO Stocks"]
# for sec in sectors["Sector"].head(17):
# for sec in sectors["Sector"].tail(1):
# for sec in sectors.loc[5:17,"Sector"]:
for sec in sectors:
    print(sec)
    stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector=sec))
    stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
    for stock in stocks_of_sector["symbol"]:
        # get_uptrend(stock)
        # get_flat(stock)
        stock = stock.split(".")[0]
        data = nse.get_equity_option_chain(stock)
        analyze_stock(data, stock)

# get_flat("HCLTECH.NS")
# res = list(set(res))
# print(f"final result {res}")
optionStocks["Bullish"] = sorted(
    optionStocks["Bullish"], key=lambda stock: stock["Percent"], reverse=True
)
optionStocks["Bearish"] = sorted(
    optionStocks["Bearish"], key=lambda stock: stock["Percent"], reverse=True
)
optionStocks["Bullish"] = [
    stock for stock in optionStocks["Bullish"] if stock["Percent"] > 60
]
bull = pd.DataFrame(optionStocks["Bullish"])
bull.to_csv("bull.csv")
optionStocks["Bearish"] = [
    stock for stock in optionStocks["Bearish"] if stock["Percent"] < 40
]
bear = pd.DataFrame(optionStocks["Bearish"])
bear.to_csv("bear.csv")
