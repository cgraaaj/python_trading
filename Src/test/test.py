import sys
import json
from datetime import datetime
import os
import subprocess
import time
from dateutil import tz
import pandas as pd
import numpy as np
import datetime as dt

sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")
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
# nse = Nse()
# stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector="FO Stocks"))
# stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
# finaldf = pd.DataFrame()
# dflist = []
# dict = {}

# dri = Driver()


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

date = '09-JUL-2021'
print(datetime.strptime(date, "%d-%b-%Y")<datetime.today() - dt.timedelta(days=14))