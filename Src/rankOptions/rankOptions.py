import sys
import os

sys.path.append("/home/pudge/Trading/python_trading/Src")

from configparser import ConfigParser
import nse
from multiprocessing import Pool
import multiprocessing
from itertools import repeat
from oiAnalyze import analyze_stock
from pprint import pprint
import get_db
from datetime import datetime


class OptionTrend:
    def __init__(self):
        self.result = multiprocessing.Manager().list()
        self.analyzing = True

    def analyze_options_data(self, index, symbol):
        url = nse.option_chain_url.format(index, symbol)
        try:
            resp = nse.get_nse_response(url)
            resp = analyze_stock(resp["records"]["expiryDates"][0], resp["records"])
            # pprint(resp)
            temp = {}
            temp["name"] = symbol
            temp["options"] = {
                "calls": {"bullish": 0, "bearish": 0},
                "puts": {"bullish": 0, "bearish": 0},
            }
            temp["options"]["calls"]["bullish"] = len(
                resp[resp["Call Trend"] == "Bullish"]
            )
            temp["options"]["calls"]["bearish"] = len(
                resp[resp["Call Trend"] == "Bearish"]
            )
            temp["options"]["puts"]["bullish"] = len(
                resp[resp["Put Trend"] == "Bullish"]
            )
            temp["options"]["puts"]["bearish"] = len(
                resp[resp["Put Trend"] == "Bearish"]
            )
            temp["callTrend"] = (
                True
                if temp["options"]["calls"]["bullish"]
                > temp["options"]["calls"]["bearish"]
                else False
            )
            temp["putTrend"] = (
                True
                if temp["options"]["puts"]["bullish"]
                > temp["options"]["puts"]["bearish"]
                else False
            )
            self.result.append(temp)
        except Exception as e:
            print(symbol + " " + str(e))

    def get_option_trend(self, mode):
        tickers = (
            ["NIFTY", "BANKNIFTY", "FINNIFTY"]
            if mode == "indices"
            else nse.get_nse_response(nse.equities_url)
        )
        # for ticker in tickers[:10]:
        #     self.analyze_options_data(mode, ticker)
        pool = Pool(2)
        pool.starmap(self.analyze_options_data, zip(repeat(mode), tickers[:100]))
        pool.close()
        pool.join()
        # time.sleep(5)
        # self.analyzing=False
        # pool.starmap(func, [(1, 1), (2, 1), (3, 1)])
        # pool.starmap(func, zip(a_args, repeat(second_arg)))
        # pool.map(partial(func, b=second_arg), a_args)
        # print(self.result)
        # print([ticker['name'] for ticker in self.result if ticker['callTrend']])
        # print([ticker['name'] for ticker in self.result if ticker['putTrend']])
        # return self.result

    def get_result(self):
        return self.result

currDir = os.path.dirname(os.path.abspath(__file__))
configFile = os.path.join(currDir, 'config.cfg')
optionTrend = OptionTrend()
config = ConfigParser()
config.read(configFile)
session = config.get('DEFAULT','sessionCounter')
# session = config['DEFAULT']['sessionCounter']
optionTrend.get_option_trend("equities")
result = optionTrend.get_result()

top5_call = [
    ticker
    for ticker in sorted(
        result, key=lambda ticker: ticker["options"]["calls"]["bullish"], reverse=True
    )
][:5]
top5_put = [
    ticker
    for ticker in sorted(
        result, key=lambda ticker: ticker["options"]["puts"]["bullish"], reverse=True
    )
][:5]

db = get_db.get_database()
collection = db["rankOptions"]
date = datetime.today().strftime("%d-%m-%Y")
res = list(collection.find({"date": date}))

if not res:
    data = {}
    data["date"] = date
    sessions = []
    sessionData = {}
    sessionData["session"] = session
    sessionData["options"] = {"call": top5_call, "put": top5_put}
    sessions.append(sessionData)
    data["sessions"] = sessions
    data["last_modified"] = datetime.utcnow()
    collection.insert_one(data)
    
else:
    currData = res[0]
    sessions = currData["sessions"]
    sessionData = {}
    sessionData["session"] = session
    sessionData["options"] = {"call": top5_call, "put": top5_put}
    sessions.append(sessionData)
    currData["last_modified"] = datetime.utcnow()
    collection.update_one({"date": date}, {"$set": {"sessions": sessions}})

config.set('DEFAULT', 'sessionCounter', str(int(session)+1))
with open(configFile, 'w') as cfg:
    config.write(cfg)
