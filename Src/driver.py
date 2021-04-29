import pandas as pd
import datetime as dt
import logging
import os
import multiprocessing
import numpy as np
import pandas as pd


from sector import Sector
from dateutil.relativedelta import relativedelta
from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse

# from alpha_vantage.techindicators import TechIndicators

LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))

# logging.basicConfig(
#     filename="{}/logs/".format(LOCATE_PY_DIRECTORY_PATH)
#     + dt.datetime.now().strftime("%d-%m-%Y")
#     + ".log",
#     format="[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
#     datefmt="%m-%d %H:%M:%S",
#     level=logging.INFO,
#     filemode="w",
# )
# logger = logging.getLogger(__name__)

log_formatter = logging.Formatter(
    "%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    "%m-%d %H:%M:%S",
)


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(log_formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger


logger = setup_logger(
    "default",
    "{}/logs/".format(LOCATE_PY_DIRECTORY_PATH)
    + dt.datetime.now().strftime("%d-%m-%Y")
    + ".log",
)

logger_tele = setup_logger(
    "tele",
    "{}/logs_tele/".format(LOCATE_PY_DIRECTORY_PATH)
    + dt.datetime.now().strftime("%d-%m-%Y")
    + "-tele.log",
)


class Driver:
    def __init__(self):
        # alphaVantage key
        # ti = TechIndicators(open('Src/alphaVantage_key.txt', 'r').read())
        # BSE data
        # bseData = pd.read_csv('/home/pudge/Desktop/PROJECTS/Python/trading/test/source.csv')
        self.res = multiprocessing.Manager().list()
        self.days_high_dict = multiprocessing.Manager().dict()
        self.list_sector = multiprocessing.Manager().list()
        self.exception = []
        self.today = dt.date.today()
        self.nse = Nse()
        # self.strategies = {
        #     "Seven Day SMA200": {"fun": self.get_seven_day_low_sma200, "kwargs": {}}
        # }

    # returns the indices which has ltp near to sma200 and low in last 7days refer this link https://www.youtube.com/watch?v=_9Bmxylp63Y
    def get_seven_day_low_sma200(self, ticker="CUB.NS"):
        # logger.info("Stock is :" + ticker)
        sev_data = yf(ticker, result_range="7d", interval="1d").result
        if sev_data.iloc[-1]["Close"] <= sev_data.iloc[0]["Close"]:
            ticker_data = yf(ticker, result_range="400d", interval="1d").result
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
                    self.res.append(ticker.split(".")[0])
            else:
                self.exception.append(ticker.split(".")[0])

    # returns the indices which has ltp near to sma200 and high in last 7days
    def get_seven_day_high_sma200(self, ticker="CUB.NS"):
        sev_data = yf(ticker, result_range="7d", interval="1d").result
        if sev_data.iloc[-1]["Close"] >= sev_data.iloc[0]["Close"]:
            self.res.append(ticker.split(".")[0])

    # returns the index of whose fastSMA cuts its slowSMA in last 4 days
    def get_sma_slowFast(self, ticker="CUB.NS", slow=200, fast=50):
        # logger.info("Stock :"+ticker)
        ticker_data = yf(
            ticker, result_range=str((slow * 2)) + "d", interval="1d"
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
                self.res.append(ticker.split(".")[0])

    # returns the index for which the price will fall on (or) above the sma within last 40 days
    def support_sma(self, ticker="CUB.NS", support=50):
        months = 3
        ticker_data = yf(
            ticker,
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
            self.res.append(ticker.split(".")[0])

    # returns the stocks which breaks the day's high at 10'o Clock
    def get_todays_stock(self, ticker="CUB.NS"):
        ticker_data = yf(ticker, result_range="1d", interval="1m").result
        if ticker_data.iloc[-2]["Close"] > self.days_high_dict[ticker]["high"]:

            data = {
                "stock": ticker if ".NS" not in ticker else ticker.split(".")[0],
                "day_high": self.days_high_dict[ticker]["high"],
                "brk_val": ticker_data.iloc[-2]["Close"],
                "trade": "Buy",
            }
            self.res.append(data)
            logger_tele.info(
                "{} has broke todays high {} with value {}".format(
                    ticker,
                    self.days_high_dict[ticker]["high"],
                    ticker_data.iloc[-2]["Close"],
                )
            )
        elif ticker_data.iloc[-2]["Close"] < self.days_high_dict[ticker]["low"]:
            data = {
                "stock": ticker if ".NS" not in ticker else ticker.split(".")[0],
                "day_low": self.days_high_dict[ticker]["low"],
                "brk_val": ticker_data.iloc[-2]["Close"],
                "trade": "Sell",
            }
            self.res.append(data)
            logger_tele.info(
                "{} has broke todays low {} with value {}".format(
                    ticker,
                    self.days_high_dict[ticker]["low"],
                    ticker_data.iloc[-2]["Close"],
                )
            )

    # sets days high of a ticker
    def days_high_low(self, ticker="CUB.NS"):
        ticker_data = yf(ticker, result_range="1d", interval="15m").result
        self.days_high_dict[ticker] = {
            "high": ticker_data.head(3)["High"].max(),
            "low": ticker_data.head(3)["Low"].min(),
        }

    def get_ticker_data(self, interval, range, ticker="CUB.NS"):
        ticker_data = yf(ticker, result_range=range, interval=interval).result
        return ticker_data

    # loops through the sectors for indices
    def run_strategy(self, strategy, sec="Nifty 50", *args, **kwargs):
        # print('XXXXXXXXXXXXXXX{}XXXXXXXXXXXXXXXX'.format(sec))
        if type(sec) is list:
            stocks_of_sector = pd.DataFrame(sec, columns=["symbol"])
        else:
            if "days_high_break" not in strategy.__name__:
                logger.info("Sector: " + sec)
            stocks_of_sector = pd.DataFrame(self.nse.get_stocks_of_sector(sector=sec))
            # check the manual watchlist file has some data
            if (
                os.stat(
                    "{}/data/watchlist.txt".format(LOCATE_PY_DIRECTORY_PATH)
                ).st_size
                != 0
            ):
                watchlist = open(
                    "{}/data/watchlist.txt".format(LOCATE_PY_DIRECTORY_PATH), "r"
                )
                # removes /n or empty spaces for each stock
                watchlist = [stock.strip() for stock in watchlist]
                # adds watchlist to the actual stocks of sector
                stocks_of_sector = stocks_of_sector.append(
                    pd.DataFrame(watchlist, columns=["symbol"]), ignore_index=True
                )
            stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(
                lambda x: x + ".NS"
            )
        processes = []
        for ticker in stocks_of_sector["symbol"]:
            p = multiprocessing.Process(target=strategy, args=[ticker], kwargs=kwargs)
            p.start()
            processes.append(p)
        for pros in processes:
            pros.join()
        # with concurrent.futures.ProcessPoolExecutor() as executor:
        # [
        #     executor.submit(strategy, id, **kwargs)
        #     for id in stocks_of_sector["symbol"]
        # ]
        # executor.map(strategy, stocks_of_sector["symbol"])

        # stocks_of_sector["symbol"].apply(lambda x: strategy(ticker=x, **kwargs))
        if len(self.res) > 0:
            sector = Sector(sec, list(self.res))
            # logger.info("sector: " + json.dumps(sector.__dict__))
            self.list_sector.append(sector.__dict__)
            self.res = multiprocessing.Manager().list()

    # returns result and exception if any
    @property
    def result(self):
        # return {'stocks':list(set(self.res)),'excep':list(set(self.exception))}
        return self.list_sector

    @property
    def day_high_dict(self):
        return self.days_high_dict

    @result.setter
    def result(self, value):
        # return {'stocks':list(set(self.res)),'excep':list(set(self.exception))}
        self.list_sector = multiprocessing.Manager().list()

    # returns available strategies
    @property
    def strategies(self):
        return {
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