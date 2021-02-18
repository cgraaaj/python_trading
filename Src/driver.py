import pandas as pd
import datetime as dt
import logging
import os
import sys
import json

from sector import Sector
from dateutil.relativedelta import relativedelta
from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse

# from alpha_vantage.techindicators import TechIndicators

LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))

logging.basicConfig(
    filename="{}/logs/".format(LOCATE_PY_DIRECTORY_PATH)
    + dt.datetime.now().strftime("%d-%m-%Y")
    + ".log",
    format="[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    datefmt="%m-%d %H:%M:%S",
    level=logging.INFO,
    filemode="w",
)
logger = logging.getLogger(__name__)


class Driver:
    def __init__(self):
        # alphaVantage key
        # ti = TechIndicators(open('Src/alphaVantage_key.txt', 'r').read())
        # BSE data
        # bseData = pd.read_csv('/home/pudge/Desktop/PROJECTS/Python/trading/test/source.csv')
        self.res = []
        self.list_sector = []
        self.exception = []
        self.today = dt.date.today()
        self.nse = Nse()
        self.strategies = {
            "Slow fast SMA": {
                "fun": self.get_sma_slowFast,
                "kwargs": {"slow": 100, "fast": 30},
            },
            "Seven Day Low SMA200": {
                "fun": self.get_seven_day_low_sma200,
                "kwargs": {},
            },
            "Seven Day High SMA200": {
                "fun": self.get_seven_day_high_sma200,
                "kwargs": {},
            },
        }
        # self.strategies = {
        #     "Seven Day SMA200": {"fun": self.get_seven_day_low_sma200, "kwargs": {}}
        # }

    # returns the indices which has ltp near to sma200 and low in last 7days refer this link https://www.youtube.com/watch?v=_9Bmxylp63Y
    def get_seven_day_low_sma200(self, ticker="CUB"):
        # logger.info("Stock is :" + ticker)
        sev_data = yf(ticker + ".NS", result_range="7d", interval="1d").result
        if sev_data.iloc[-1]["Close"] <= sev_data.iloc[0]["Close"]:
            ticker_data = yf(ticker + ".NS", result_range="400d", interval="1d").result
            ticker_data["sma_200"] = ticker_data["Close"].rolling(window=200).mean()
            if len(ticker_data.index) > 1:
                if (
                    ticker_data.iloc[-2]["sma_200"] > ticker_data.iloc[-2]["Close"]
                    and ticker_data.iloc[-2]["sma_200"]
                    < (
                        ticker_data.iloc[-2]["Close"]
                        + (ticker_data.iloc[-2]["Close"] * 0.015)
                    )
                ) or (
                    ticker_data.iloc[-2]["sma_200"]
                    > (
                        ticker_data.iloc[-2]["Close"]
                        + (ticker_data.iloc[-2]["Close"] * 0.015)
                    )
                    and ticker_data.iloc[-2]["sma_200"] < ticker_data.iloc[-2]["Close"]
                ):
                    self.res.append(ticker)
            else:
                self.exception.append(ticker)

    # returns the indices which has ltp near to sma200 and high in last 7days
    def get_seven_day_high_sma200(self, ticker="CUB"):
        sev_data = yf(ticker + ".NS", result_range="7d", interval="1d").result
        if sev_data.iloc[-1]["Close"] >= sev_data.iloc[0]["Close"]:
            self.res.append(ticker)

    # returns the index of whose fastSMA cuts its slowSMA in last 4 days
    def get_sma_slowFast(self, ticker="CUB", slow=200, fast=50):
        # logger.info("Stock :"+ticker)
        ticker_data = yf(
            ticker + ".NS", result_range=str((slow * 2)) + "d", interval="1d"
        ).result
        ticker_data["sma_fast"] = (
            ticker_data.iloc[(slow * 2) - (fast * 2) :]["Close"]
            .rolling(window=fast)
            .mean()
        )
        ticker_data["sma_slow"] = ticker_data["Close"].rolling(window=slow).mean()
        ticker_data["sma_diff"] = ticker_data["sma_slow"] - ticker_data["sma_fast"]
        data = ticker_data[ticker_data["sma_diff"] <= (ticker_data["sma_slow"] * 0.005)]
        if len(data) >= 1:
            data = data.index[0]
            if ticker_data.iloc[
                ticker_data.index.get_loc(data)
            ].name > self.today - dt.timedelta(days=4):
                self.res.append(ticker)

    # returns the index for which the price will fall on (or) above the sma within last 40 days
    def support_sma(self, ticker="CUB", support=50):
        months = 3
        ticker_data = yf(
            ticker + ".NS",
            result_range=str((months * 30) + support) + "d",
            interval="1d",
        ).result
        ticker_data["sma"] = (
            ticker_data["Close"].iloc[50:].rolling(window=support).mean()
        )
        ticker_data = ticker_data[ticker_data["sma"] > 1]
        sma_diff = (ticker_data["Close"] > ticker_data["sma"]) & (
            ticker_data["Close"] < (ticker_data["sma"] + (ticker_data["Close"] * 0.05))
        )
        res = ticker_data[sma_diff].index.date > self.today - relativedelta(months=2)
        if len(res) > 30:
            self.res.append(ticker)

    # loops through the sectors for indices
    def run_strategy(self, strategy, sec="Nifty 50", *args, **kwargs):
        # print('XXXXXXXXXXXXXXX{}XXXXXXXXXXXXXXXX'.format(sec))
        logger.info("Sector: " + sec)
        stocks_of_sector = pd.DataFrame(self.nse.get_stocks_of_sector(sector=sec))
        stocks_of_sector["symbol"].apply(lambda x: strategy(ticker=x, **kwargs))
        if len(self.res) > 0:
            sector = Sector(sec, self.res)
            # logger.info("sector: " + json.dumps(sector.__dict__))
            self.list_sector.append(sector.__dict__)
            self.res = []

    # returns result and exception if any
    def get_result(self):
        # return {'stocks':list(set(self.res)),'excep':list(set(self.exception))}
        return self.list_sector

    def set_result(self):
        # return {'stocks':list(set(self.res)),'excep':list(set(self.exception))}
        self.list_sector = []

    # returns available strategies
    def get_strategies(self):
        return self.strategies