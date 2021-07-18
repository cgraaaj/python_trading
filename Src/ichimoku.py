import sys
import json
from datetime import datetime
import os
import subprocess
import time
from dateutil import tz
import pandas as pd
import numpy as np

sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")
from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse
from driver import Driver
from telegram_helper import Tele
import math

nse = Nse()
stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
finaldf = pd.DataFrame()
dflist = []
dict = {}
dri = Driver()
stocks_buy = []
stocks_sell = []

# Ichimoku
def get_Ichimoku(
    pd,
    tenkan_lookback,
    kijunsen_lookback,
    senkou_span_b_lookback,
    chikou_span_lookfront,
):
    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    period9_high = pd["High"].rolling(window=tenkan_lookback).max()
    period9_low = pd["Low"].rolling(window=tenkan_lookback).min()
    pd["tenkan_sen"] = (period9_high + period9_low) / 2

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    period26_high = pd["High"].rolling(window=kijunsen_lookback).max()
    period26_low = pd["Low"].rolling(window=kijunsen_lookback).min()
    pd["kijun_sen"] = (period26_high + period26_low) / 2

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    pd["senkou_span_a"] = ((pd["tenkan_sen"] + pd["kijun_sen"]) / 2).shift(26)

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    period52_high = pd["High"].rolling(window=senkou_span_b_lookback).max()
    period52_low = pd["Low"].rolling(window=senkou_span_b_lookback).min()
    pd["senkou_span_b"] = ((period52_high + period52_low) / 2).shift(26)

    # The most current closing price plotted 22 time periods behind (optional)
    pd["chikou_span"] = pd["Close"].shift(
        -chikou_span_lookfront
    )  # 22 according to investopedia

    return pd


# GET THE DAYS RESULT P/L


def check_stock(stock):
    print(f"checking {stock}")
    rnge = 5
    ticker_data = dri.get_ticker_data(
        ticker=stock, range=str(rnge) + "d", interval="15m"
    )
    print(ticker_data)
    # exit()
    ticker_data = get_Ichimoku(ticker_data, 9, 26, 52, 26)
    ticker_data = ticker_data.iloc[100:]
    print(ticker_data)
    buy_condition = (
        # (ticker_data["tenkan_sen"] > ticker_data["kijun_sen"])
        # (
        #     (ticker_data["tenkan_sen"] > ticker_data["kijun_sen"])
        #     & (
        #         ticker_data["tenkan_sen"].shift(1)
        #         <= ticker_data["kijun_sen"].shift(1)
        #     )
        # )
        # & 
        (
            (ticker_data["Close"] > ticker_data["senkou_span_a"])
            & (ticker_data["Close"] > ticker_data["senkou_span_b"])
        )
        # & (
        #     (ticker_data["tenkan_sen"] > ticker_data["senkou_span_a"])
        #     & (ticker_data["tenkan_sen"] > ticker_data["senkou_span_b"])
        # )
        # & (
        #     (ticker_data["kijun_sen"] > ticker_data["senkou_span_a"])
        #     & (ticker_data["kijun_sen"] > ticker_data["senkou_span_b"])
        # )
        # & (ticker_data["chikou_span"].shift(-26) > ticker_data["Close"].shift(-26))
    )
    # buy_data = ticker_data[np.where(buy_condition, True, False)]
    buy_data = ticker_data[buy_condition]
    if not buy_data.empty:
        # get the lastest breakout of the day
        breakout_time = buy_data.index.values[len(buy_data.index.values)-2]
        # check the breakout is happend now(-5 mins)
        if breakout_time == ticker_data.index.values[len(ticker_data.index.values)-2]:
            stocks_buy.append(stock)
    sell_condition = (
        # (ticker_data["tenkan_sen"] < ticker_data["kijun_sen"])
        # (
        #     (ticker_data["tenkan_sen"] < ticker_data["kijun_sen"])
        #     & (
        #         ticker_data["tenkan_sen"].shift(1)
        #         >= ticker_data["kijun_sen"].shift(1)
        #     )
        # )
        # & 
        # (
        #     (ticker_data["tenkan_sen"] < ticker_data["senkou_span_a"])
        #     & (ticker_data["tenkan_sen"] < ticker_data["senkou_span_b"])
        # )
        # & (
        #     (ticker_data["kijun_sen"] < ticker_data["senkou_span_a"])
        #     & (ticker_data["kijun_sen"] < ticker_data["senkou_span_b"])
        # )
        # & 
        (
            (ticker_data["Close"] < ticker_data["senkou_span_a"])
            & (ticker_data["Close"] < ticker_data["senkou_span_b"])
        )
        # & (ticker_data["chikou_span"].shift(-26) < ticker_data["Close"].shift(-26))
    )
    # sell_data = ticker_data[np.where(sell_condition, True, False)]
    sell_data = ticker_data[sell_condition]
    if not sell_data.empty:
        # get the lastest breakout of the day
        breakout_time = sell_data.index.values[len(sell_data.index.values)-2]
        # print(breakout_time)
        # check the breakout is happend now(-5 mins)
        if breakout_time == ticker_data.index.values[len(ticker_data.index.values)-2]:
            stocks_sell.append(stock)
    
    # tele = Tele(stocks_buy)
    # tele.send_message(f"Stocksto buy...")
    # tele = Tele(stocks_sell)
    # tele.send_message(f"Stocksto sell...")


def get_stocks(trade):
    if trade == "equity":
        stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
        stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
        for stock in stocks_of_sector["symbol"]:
            check_stock(stock)
    elif trade == "bitcoin":
        marketcap_BTCs_INR = "BTC-INR,ETH-INR,BNB-INR,XRP-INR,USDT-INR,ADA-INR,DOGE-INR,DOT1-INR,UNI3-INR,LTC-INR,LINK-INR,BCH-INR,THETA-INR,XLM-INR,FIL-INR,USDC-INR,VET-INR,TRX-INR,EOS-INR,SOL1-INR,BSV-INR,MIOTA-INR,LUNA1-INR,CRO-INR"
        marketcap_BTCs_USD = "BTC-USD,ETH-USD,BNB-USD,XRP-USD,USDT-USD,ADA-USD,DOT1-USD,DOGE-USD,LTC-USD,BCH-USD,UNI3-USD,LINK-USD,VET-USD,XLM-USD,THETA-USD,FIL-USD,TRX-USD,USDC-USD,BSV-USD,EOS-USD,SOL1-USD,MIOTA-USD,NEO-USD,BTT1-USD"
        for BTC in marketcap_BTCs_INR.split(","):
            check_stock(BTC)
    else:
        print("Give arguments like equity or bitcoin")
    # check_stocks("ROUTE.NS")
    return {'buy':stocks_buy,'sell':stocks_sell}

# check_stock("ROUTE.NS")
# print(stocks_buy)
# print(stocks_sell)