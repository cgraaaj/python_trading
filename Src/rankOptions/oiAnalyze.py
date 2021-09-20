import pandas as pd
import numpy as np
import os


def oi_action_ce(row):
    if row["Call Price Change"] > 0 and row["Call Change in OI"] > 0:
        return "Long Buildup"
    elif row["Call Price Change"] > 0 and row["Call Change in OI"] < 0:
        return "Short Cover"
    elif row["Call Price Change"] < 0 and row["Call Change in OI"] > 0:
        return "Short Buildup"
    elif row["Call Price Change"] < 0 and row["Call Change in OI"] < 0:
        return "Long Unwind"


def oi_action_pe(row):
    if row["Put Price Change"] > 0 and row["Put Change in OI"] > 0:
        return "Long Buildup"
    elif row["Put Price Change"] > 0 and row["Put Change in OI"] < 0:
        return "Short Cover"
    elif row["Put Price Change"] < 0 and row["Put Change in OI"] > 0:
        return "Short Buildup"
    elif row["Put Price Change"] < 0 and row["Put Change in OI"] < 0:
        return "Long Unwind"


def analyze_stock(expiry, data):
    data_path = os.path.dirname(os.path.realpath(__file__))
    expiry_data = {}
    df_ce_pe = pd.DataFrame()
    buillish = ["Short Cover", "Long Buildup"]
    bearish = ["Long Unwind", "Short Buildup"]
    columns = [
        "Call OI",
        "Call Change in OI",
        "Call Volume",
        "Call LTP",
        "Call Price Change",
        "Strike Price",
        "Put Price Change",
        "Put LTP",
        "Put Volume",
        "Put Change in OI",
        "Put OI",
    ]
    expiry_dates = data["expiryDates"]
    for expiry_dt in expiry_dates:
        expiry_data[expiry_dt] = [
            d for d in data["data"] if expiry_dt in d["expiryDate"]
        ]
    ce = [expd.get("CE") for expd in expiry_data[expiry] if "CE" in expd.keys()]
    pe = [expd.get("PE") for expd in expiry_data[expiry] if "PE" in expd.keys()]
    df_ce = pd.DataFrame(ce)[
        [
            "openInterest",
            "changeinOpenInterest",
            "totalTradedVolume",
            "lastPrice",
            "change",
            "strikePrice",
        ]
    ]
    df_pe = pd.DataFrame(pe)[
        [
            "strikePrice",
            "change",
            "lastPrice",
            "totalTradedVolume",
            "changeinOpenInterest",
            "openInterest",
        ]
    ]
    df_ce_pe = (
        pd.merge(df_ce, df_pe, how="outer", on="strikePrice").fillna(0.0).round(2)
    )
    df_ce_pe.columns = columns
    # sends each row axis = 1
    df_ce_pe["Call OI Action"] = df_ce_pe.apply(oi_action_ce, axis=1)
    df_ce_pe["Put OI Action"] = df_ce_pe.apply(oi_action_pe, axis=1)
    df_ce_pe["Call Trend"] = np.where(
        df_ce_pe["Call OI Action"].isin(buillish),
        "Bullish",
        np.where(df_ce_pe["Call OI Action"].isin(bearish), "Bearish", None),
    )
    df_ce_pe["Put Trend"] = np.where(
        df_ce_pe["Put OI Action"].isin(buillish),
        "Bullish",
        np.where(df_ce_pe["Put OI Action"].isin(bearish), "Bearish", None),
    )
    columns.insert(0, "Call Trend")
    columns.insert(1, "Call OI Action")
    columns.insert(len(df_ce_pe.columns) - 1, "Put OI Action")
    columns.insert(len(df_ce_pe.columns), "Put Trend")
    df_ce_pe = df_ce_pe[columns]
    return df_ce_pe
