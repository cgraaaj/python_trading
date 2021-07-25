import sys
import pandas as pd
import numpy as np
import matplotlib.pylab as plb
from matplotlib import pyplot as plt
from dateutil import tz
from pprint import pprint
from pandas.plotting import table
from datetime import datetime
import os

sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")
from telegram_helper import Tele
from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse
from driver import Driver


class OIAction:
    def __init__(self,stock):
        self.nse = Nse()
        self.stock = stock
        self.expiry_data = {}
        self.data_path = f'/home/pudge/Trading/python_trading/Src/test/OIAction/data/{stock}'
        os.mkdir(self.data_path)
        self.columns = [
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
        self.df_ce_pe = pd.DataFrame()
        self.buillish = ["Short Cover", "Long Buildup"]
        self.bearish = ["Long Unwind", "Short Buildup"]

    def oi_action_ce(self, row):
        if row["Call Price Change"] > 0 and row["Call Change in OI"] > 0:
            return "Long Buildup"
        elif row["Call Price Change"] > 0 and row["Call Change in OI"] < 0:
            return "Short Cover"
        elif row["Call Price Change"] < 0 and row["Call Change in OI"] > 0:
            return "Short Buildup"
        elif row["Call Price Change"] < 0 and row["Call Change in OI"] < 0:
            return "Long Unwind"

    def oi_action_pe(self, row):
        if row["Put Price Change"] > 0 and row["Put Change in OI"] > 0:
            return "Long Buildup"
        elif row["Put Price Change"] > 0 and row["Put Change in OI"] < 0:
            return "Short Cover"
        elif row["Put Price Change"] < 0 and row["Put Change in OI"] > 0:
            return "Short Buildup"
        elif row["Put Price Change"] < 0 and row["Put Change in OI"] < 0:
            return "Long Unwind"

    def analyze_stock(self):
        data = self.nse.get_equity_option_chain(equity=self.stock)
        expiry_dates = data["records"]["expiryDates"]
        for expiry_dt in expiry_dates:
            self.expiry_data[expiry_dt] = [
                d for d in data["records"]["data"] if expiry_dt in d["expiryDate"]
            ]
        ce = [
            expd["CE"]
            for expd in self.expiry_data[expiry_dates[0]]
            if "CE" in expd.keys()
        ]
        pe = [
            expd["PE"]
            for expd in self.expiry_data[expiry_dates[0]]
            if "PE" in expd.keys()
        ]
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
        self.df_ce_pe = (
            pd.merge(df_ce, df_pe, how="outer", on="strikePrice").fillna(0.0).round(2)
        )
        self.df_ce_pe.columns = self.columns
        # sends each row axis = 1
        self.df_ce_pe["Call OI Action"] = self.df_ce_pe.apply(self.oi_action_ce, axis=1)
        self.df_ce_pe["Put OI Action"] = self.df_ce_pe.apply(self.oi_action_pe, axis=1)
        self.df_ce_pe["Call Trend"] = np.where(
            self.df_ce_pe["Call OI Action"].isin(self.buillish),
            "Bullish",
            np.where(
                self.df_ce_pe["Call OI Action"].isin(self.bearish), "Bearish", None
            ),
        )
        self.df_ce_pe["Put Trend"] = np.where(
            self.df_ce_pe["Put OI Action"].isin(self.buillish),
            "Bullish",
            np.where(
                self.df_ce_pe["Put OI Action"].isin(self.bearish), "Bearish", None
            ),
        )
        self.columns.insert(0, "Call Trend")
        self.columns.insert(1, "Call OI Action")
        self.columns.insert(len(self.df_ce_pe.columns) - 1, "Put OI Action")
        self.columns.insert(len(self.df_ce_pe.columns), "Put Trend")
        self.df_ce_pe = self.df_ce_pe[self.columns]
        return self.df_ce_pe
    
    def generate_xsls(self):
        self.df_ce_pe.to_excel(f'{self.data_path}/{self.stock}.xsls')

    def generate_df_to_img(self):
        # set fig size
        fig, ax = plb.subplots(figsize=(18, 10)) 
        # no axes
        ax.xaxis.set_visible(False)  
        ax.yaxis.set_visible(False)  
        # no frame
        ax.set_frame_on(False)  
        # plot table
        tab = table(ax, self.df_ce_pe, loc='upper right')  
        # set font manually
        tab.auto_set_font_size(False)
        tab.set_fontsize(8) 
        # save the result
        plt.savefig(f'{self.data_path}/{self.stock}_df.png')

    def generate_oi_strike_png(self):
        oi_call = self.df_ce_pe['Call OI'].to_list()
        oi_put = self.df_ce_pe['Put OI'].to_list()
        index = self.df_ce_pe['Strike Price'].to_list()
        df = pd.DataFrame({'Call OI':oi_call,'Put OI':oi_put},index=index)
        plt.rcParams["figure.figsize"] = [15, 10]
        df.plot(kind='bar')
        plt.xticks(rotation=30, horizontalalignment="center")
        plt.savefig(f'{self.data_path}/{self.stock}_oi_strike.png')
        plt.title(f'{self.stock} OI vs Strike Price')
        plt.xlabel("Strike Price")
        plt.ylabel("OI Call/Put")
    
    def generate_change_in_oi_strike_png(self):
        oi_call = self.df_ce_pe['Call Change in OI'].to_list()
        oi_put = self.df_ce_pe['Put Change in OI'].to_list()
        index = self.df_ce_pe['Strike Price'].to_list()
        df = pd.DataFrame({'Call Change in OI':oi_call,'Put Change in OI':oi_put},index=index)
        plt.rcParams["figure.figsize"] = [15, 10]
        df.plot(kind='bar')
        plt.xticks(rotation=30, horizontalalignment="center")
        plt.savefig(f'{self.data_path}/{self.stock}_change_in_oi_strike.png')
        plt.title(f'{self.stock} Change in OI vs Strike Price')
        plt.xlabel("Strike Price")
        plt.ylabel("Change in OI Call/Put")
