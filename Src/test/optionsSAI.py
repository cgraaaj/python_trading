import requests
import numpy as np
import time
import talib
import json
import pandas as pd
import logging
from time import sleep
from datetime import datetime
import datetime
from kiteconnect import KiteConnect

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", -1)

# set your zerodha credentials

api_key = "your api_key"
access_token = "your access_token"
kite = KiteConnect(api_key=api_key)
kite.set_access_token(access_token)

dt = datetime.datetime.now()
curr_day_dt = dt.strftime("%Y-%m-%d %H:%M:%S")
print(curr_day_dt)
curr_day = dt.strftime("%Y-%m-%d")
# curr_day='2021-01-29'
print("Current date is ")
print(curr_day)
dt += datetime.timedelta(days=-5)
prev_day_dt = dt.strftime("%Y-%m-%d %H:%M:%S")

df = pd.DataFrame(kite.historical_data(256265, prev_day_dt, curr_day_dt, "day"))
prev_date = df["date"].iloc[-2]
print("Previous date is")
prev_day_dt = prev_date.strftime("%Y-%m-%d")
print(prev_day_dt)


def get_data():

    for instr in ["NIFTY"]:
        try:
            print("downloading instruments tokens.....")
            df = pd.read_csv("https://api.kite.trade/instruments")
            print("instruments tokens downloded.....")
            df = df[df["segment"] == "NFO-OPT"]
            df = df[df["name"] == "NIFTY"]
            df["expiry"] = pd.to_datetime(df["expiry"])
            tday = pd.Timestamp.today() - pd.DateOffset(5)
            print(tday)
            df = df[~(df["expiry"] <= tday)]
            df = df[df.expiry == df.expiry.min()]
            print(df)
        except Exception as e:
            print(e)

    spot_price = kite.ltp("NSE:NIFTY 50")
    spot_price = str(spot_price["NSE:NIFTY 50"]["last_price"])
    print(spot_price)
    expiry = df["expiry"].iloc[0]
    day = expiry.strftime("%d")
    month = expiry.strftime("%m")
    year = expiry.strftime("%y")
    print(expiry)
    expiry_dt = str(year) + str(int(month)) + str(day)
    print(expiry_dt)
    # expiry_dt='21APR'

    atm_value = int(round(int(float(spot_price)) / 100, 0) * 100)
    ce_itm_value = atm_value - 50
    ce_deep_itm_value = atm_value - 100
    ce_otm_value = atm_value + 50
    CE_atm_strike = "NIFTY" + expiry_dt + str(atm_value) + "CE"
    CE_itm_strike = "NIFTY" + expiry_dt + str(ce_itm_value) + "CE"
    CE_deep_itm_strike = "NIFTY" + expiry_dt + str(ce_deep_itm_value) + "CE"
    CE_otm_strike = "NIFTY" + expiry_dt + str(ce_otm_value) + "CE"

    pe_itm_value = atm_value + 50
    pe_deep_itm_value = atm_value + 100
    pe_otm_value = atm_value - 50

    PE_atm_strike = "NIFTY" + expiry_dt + str(atm_value) + "PE"
    PE_itm_strike = "NIFTY" + expiry_dt + str(pe_itm_value) + "PE"
    PE_deep_itm_strike = "NIFTY" + expiry_dt + str(pe_deep_itm_value) + "PE"
    PE_otm_strike = "NIFTY" + expiry_dt + str(pe_otm_value) + "PE"
    print(CE_atm_strike)
    print(CE_itm_strike)
    print(CE_deep_itm_strike)
    print(CE_otm_strike)
    print(spot_price)
    print(PE_atm_strike)
    print(PE_itm_strike)
    print(PE_deep_itm_strike)
    print(PE_otm_strike)
    df = df[
        (df["tradingsymbol"] == CE_deep_itm_strike)
        | (df["tradingsymbol"] == PE_deep_itm_strike)
    ]
    tickerlist = df.tradingsymbol.values
    trade_token = df.instrument_token.values
    print(tickerlist)
    print(trade_token)
    for i in range(0, len(trade_token)):
        print(i, tickerlist[i][-7:])
        df = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
        trade_token[i]
        try:
            df = pd.DataFrame(
                kite.historical_data(
                    trade_token[i],
                    curr_day + " 09:15:00",
                    curr_day + " 15:25:00",
                    "5minute",
                )
            )
            df_prev = pd.DataFrame(
                kite.historical_data(
                    trade_token[i],
                    prev_day_dt + " 09:15:00",
                    prev_day_dt + " 15:25:00",
                    "5minute",
                )
            )
            print(df)
            if not df_prev.empty:
                df = df[["date", "open", "high", "low", "close", "volume", "oi"]]
                df["date"] = df["date"].astype(str).str[:-6]
                df_prev = df_prev[
                    ["date", "open", "high", "low", "close", "volume", "oi"]
                ]
                df_prev["date"] = df_prev["date"].astype(str).str[:-6]
            else:
                print("DF EMPTY")
        except Exception as e:
            print("  error in gethistoricaldata", trade_token[i], e)
        # print(df)
        if not df.empty:
            df_prev["vwap"] = (
                ((df_prev["high"] + df_prev["low"] + df_prev["close"]) / 3)
                * df_prev["volume"]
            ).cumsum() / df_prev["volume"].cumsum()
            df["vwap"] = (
                ((df["high"] + df["low"] + df["close"]) / 3) * df["volume"]
            ).cumsum() / df["volume"].cumsum()
            df_full = pd.concat([df_prev, df])
            df_full["vol_sma"] = talib.SMA(df_full["volume"], timeperiod=20)
            df_full["oi_sma"] = talib.SMA(df_full["oi"], timeperiod=20)
            df_full["rsi"] = talib.RSI(df_full["close"], timeperiod=14)
            df_full["vwap"] = (df_full["close"] * df_full["volume"]).cumsum() / df_full[
                "volume"
            ].cumsum()
            df_full["rsi_break"] = np.where((df_full["rsi"] > 60), True, False)
            df_full["volume_break"] = np.where(
                (df_full["volume"] > df_full["vol_sma"]), True, False
            )
            df_full["oi_break"] = np.where(
                (df_full["oi"] < df_full["oi_sma"]), True, False
            )
            df_full["vwap_break"] = np.where(
                (df_full["vwap"] < df_full["close"]), True, False
            )

            # print(df_full)
            df_full["long_positions"] = np.where(
                df_full["rsi_break"]
                & df_full["volume_break"]
                & df_full["oi_break"]
                & df_full["vwap_break"],
                1,
                0,
            )
            print(df_full)
            print(df_full["date"].iloc[-1])
            if str(df_full["long_positions"].iloc[-2]) == "1":
                message_buy = (
                    "Buy "
                    + str(tickerlist[i][-7:])
                    + " at "
                    + str(df_full["high"].iloc[-2])
                )
        time.sleep(0.05)


orderplacetime = int(9) * 60 + int(20)  # as int(hr) +60 * int(min):

timenow = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
while orderplacetime > timenow:
    time.sleep(1)
    timenow = datetime.datetime.now().hour * 60 + datetime.datetime.now().minute
    print(timenow)
while orderplacetime <= timenow:
    minute = datetime.datetime.now().minute
    second = datetime.datetime.now().second
    # print("Waiting")
    if (minute % 5) == 0 and second > 5:
        print(datetime.datetime.now())
        start_time = time.time()
        get_data()
        print("--- %s seconds ---" % (time.time() - start_time))
        sleep(220)
    elif (minute % 5) != 0:
        sleep(1)
        print("Waiting in Waiting Loop")
# get_data()
