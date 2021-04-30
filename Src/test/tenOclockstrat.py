import sys
import json
from datetime import datetime
import os
import subprocess
import time
from dateutil import tz
import pandas as pd
import numpy as np

sys.path.insert(1, "/home/pudge/Desktop/PROJECTS/Python/trading/python_trading/Src")
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


def update_portfolio(stock):
    global portfolio
    print(f"checking {stock}")
    ran = 2
    # candle = 75+26
    month_ticker_data = dri.get_ticker_data(
        ticker=stock, range=str(ran) + "mo", interval="1h"
    )
    month_ticker_data = get_Ichimoku(month_ticker_data, 9, 26, 52, 26)
    month_ticker_data = month_ticker_data.iloc[84:]
    # print(month_ticker_data)
    # exit()
    # month_ticker_data.to_csv('TVS_ITCHIMOKU.csv')
    # exit()
    # dayrange = 75*ran
    # if(leng<dayrange):
    #     print(f"{stock} has less data {leng} out of {dayrange}, hence not proceeding further")
    #     return False
    list_of_td = [
        month_ticker_data.iloc[i : i + len(month_ticker_data)] for i in range(0, len(month_ticker_data), len(month_ticker_data))
    ]
    # print(leng,len(list_of_td))
    # exit()
    for ticker_data in list_of_td:
        # buy_value = ticker_data[
        #     ticker_data["Close"] > ticker_data.head(9)["High"].max()
        # ].head(1)
        # sell_value = ticker_data[
        #     ticker_data["Close"] < ticker_data.head(9)["Low"].min()
        # ].head(1)
        # ticker_data.to_csv("tik.csv")
        buy_condition = (
            # (ticker_data["tenkan_sen"] > ticker_data["kijun_sen"])
            (
                (
                    (
                        ticker_data["tenkan_sen"].shift(1)
                        <= ticker_data["kijun_sen"].shift(1)
                    )
                    & (ticker_data["tenkan_sen"] > ticker_data["kijun_sen"])
                )
                & (
                    (ticker_data["tenkan_sen"] > ticker_data["senkou_span_a"])
                    & (ticker_data["tenkan_sen"] > ticker_data["senkou_span_b"])
                )
                & (
                    (ticker_data["kijun_sen"] > ticker_data["senkou_span_a"])
                    & (ticker_data["kijun_sen"] > ticker_data["senkou_span_b"])
                )
            )
            # | (
            #     (ticker_data["tenkan_sen"] > ticker_data["kijun_sen"])
            #     & (
            #         (ticker_data["tenkan_sen"] > ticker_data["senkou_span_a"])
            #         & (ticker_data["tenkan_sen"] > ticker_data["senkou_span_b"])
            #     )
            #     & (
            #         (ticker_data["kijun_sen"] > ticker_data["senkou_span_a"])
            #         & (ticker_data["kijun_sen"] > ticker_data["senkou_span_b"])
            #     )
            # )
            & (
                (ticker_data["Close"] > ticker_data["senkou_span_a"])
                & (ticker_data["Close"] > ticker_data["senkou_span_b"])
            )
            & (ticker_data["chikou_span"] > ticker_data["Close"].shift(26))
        )

        buy_data = ticker_data[np.where(buy_condition, True, False)]
        sell_condition = (
            # (ticker_data["tenkan_sen"] < ticker_data["kijun_sen"])
            (
                (
                    (
                        ticker_data["tenkan_sen"].shift(1)
                        >= ticker_data["kijun_sen"].shift(1)
                    )
                    & (ticker_data["tenkan_sen"] < ticker_data["kijun_sen"])
                )
                & (
                    (ticker_data["tenkan_sen"] < ticker_data["senkou_span_a"])
                    & (ticker_data["tenkan_sen"] < ticker_data["senkou_span_b"])
                )
                & (
                    (ticker_data["kijun_sen"] < ticker_data["senkou_span_a"])
                    & (ticker_data["kijun_sen"] < ticker_data["senkou_span_b"])
                )
            )
            # | (
            #     (ticker_data["tenkan_sen"] < ticker_data["kijun_sen"])
            #     & (
            #         (ticker_data["tenkan_sen"] < ticker_data["senkou_span_a"])
            #         & (ticker_data["tenkan_sen"] < ticker_data["senkou_span_b"])
            #     )
            #     & (
            #         (ticker_data["kijun_sen"] < ticker_data["senkou_span_a"])
            #         & (ticker_data["kijun_sen"] < ticker_data["senkou_span_b"])
            #     )
            # )
            & (
                (ticker_data["Close"] < ticker_data["senkou_span_a"])
                & (ticker_data["Close"] < ticker_data["senkou_span_b"])
            )
            & (ticker_data["chikou_span"] < ticker_data["Close"].shift(26))
        )

        sell_data = ticker_data[np.where(sell_condition, True, False)]
        if not buy_data.empty:
            for index, row in buy_data.iterrows():
                t = index
                buy_value = row["Close"]
                if (
                    buy_value <= 5000
                    and buy_value >= 200
                    # and t
                    # < np.datetime64(
                    #     "{} 15:00:00".format(pd.to_datetime(t).strftime("%Y-%m-%d"))
                    # )
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
                        "percent": (
                            (ticker_data.iloc[-7]["Close"] - buy_value) / buy_value
                        )
                        * 100,
                        "k": row["kijun_sen"],
                        "t": row["tenkan_sen"],
                        "sa": row["senkou_span_a"],
                        "sb": row["senkou_span_b"],
                        "c": row["chikou_span"],
                    }
                    portfolio = portfolio.append(df, ignore_index=True)
        elif not sell_data.empty:
            for index, row in buy_data.iterrows():
                t = index
                sell_value = row["Close"]
                if (
                    sell_value <= 5000
                    and sell_value >= 200
                    # and t
                    # < np.datetime64(
                    #     "{} 15:00:00".format(pd.to_datetime(t).strftime("%Y-%m-%d"))
                    # )
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
                        "percent": (
                            (sell_value - ticker_data.iloc[-7]["Close"])
                            / ticker_data.iloc[-7]["Close"]
                        )
                        * 100,
                        "k": row["kijun_sen"],
                        "t": row["tenkan_sen"],
                        "sa": row["senkou_span_a"],
                        "sb": row["senkou_span_b"],
                        "c": row["chikou_span"],
                    }
                    portfolio = portfolio.append(df, ignore_index=True)
        else:
            print(
                f"On {ticker_data.index.values[0]} this stock {stock} is in sideways, hence not added to portfolio"
            )


stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
for stock in stocks_of_sector["symbol"]:
    update_portfolio(stock)
# update_portfolio("JSWSTEEL.NS")
portfolio = portfolio.set_index("stock")
print("*******PORTFOLIO*********")
portfolio = portfolio[np.where(portfolio["time"] > np.datetime64("2021-04-23 15:00:00"),True,False)]
print(portfolio)
portfolio.to_csv("itchi.csv")
print("today's outcome:{}".format(portfolio["P/L"].sum()))