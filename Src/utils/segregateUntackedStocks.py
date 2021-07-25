import sys
import json
from datetime import datetime
import os
import subprocess
import time
from dateutil import tz
import pandas as pd
import numpy as np
import pickle
sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")
from nsetools.nse import Nse
from driver import Driver

nse = Nse()
dri = Driver()
untracked_stocks=[]
penny_stocks =[]
untracked_small_cap_stocks = []
untracked_medium_cap_stocks = []

with open ('/home/pudge/Trading/python_trading/Src/utils/pickle_data/untracked_stocks', 'rb') as fp:
    untracked_stocks = pickle.load(fp)
for stock in [stock + ".NS" for stock in untracked_stocks]:
    try:
        ticker_data = dri.get_ticker_data(
            ticker=stock, range=str(1) + "d", interval="1d"
        )
        if ticker_data.iloc[0]['Close'] < 20:
            penny_stocks.append(stock.split(".")[0])
        elif ticker_data.iloc[0]['Close'] > 20 and ticker_data.iloc[0]['Close'] < 100:
            untracked_small_cap_stocks.append(stock.split(".")[0])
        else:
            untracked_medium_cap_stocks.append(stock.split(".")[0])
    except Exception as e:
        print(e)

print(len(penny_stocks))
with open("/home/pudge/Trading/python_trading/Src/utils/pickle_data/penny_stocks", "wb") as fp:
    pickle.dump(penny_stocks, fp)

print(len(untracked_small_cap_stocks))
with open("/home/pudge/Trading/python_trading/Src/utils/pickle_data/untracked_small_cap_stocks", "wb") as fp:
    pickle.dump(untracked_small_cap_stocks, fp)

print(len(untracked_medium_cap_stocks))
with open("/home/pudge/Trading/python_trading/Src/utils/pickle_data/untracked_medium_cap_stocks", "wb") as fp:
    pickle.dump(untracked_medium_cap_stocks, fp)