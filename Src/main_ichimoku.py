import os
import json
import concurrent.futures
import telegram
import time
import sys
import pandas as pd
import math
from dotenv import load_dotenv
import datetime as dt
import logging
from datetime import datetime
from pprint import pprint
import time

from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse
from driver import Driver
from telegram_helper import Tele
import ichimoku as ichi

start_time = time.time()
trade = sys.argv[1]
data = {}
old_data = {"buy": [], "sell": []}

LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
logfile = "{0}/logs/ichi.log".format(
    LOCATE_PY_DIRECTORY_PATH, datetime.now().strftime("%d-%m-%Y")
)

if not os.path.exists(logfile):
    open(logfile, "a").close()

logging.basicConfig(
    filename=logfile,
    format="[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    datefmt="%m-%d %H:%M:%S",
    level=logging.INFO,
    filemode="w",
)
logger = logging.getLogger(__name__)

# from 10:15 to 3:30
t_end = time.time() + (60 * ((5 * 60) + 15))
sqr_off_time = time.time() + (60 * (5 * 60))
# sqr_off_time = time.time() + (60 * (5 * 60))
while time.time() < t_end:
    print(
        "the current time is {} and the end time is {}".format(
            time.strftime("%H:%M:%S", time.localtime(time.time())),
            time.strftime("%H:%M:%S", time.localtime(t_end)),
        )
    )
    temp = ichi.get_stocks(trade)
    print(temp)
    data["buy"] = list(set(old_data["buy"]) ^ set(temp["buy"]))
    data["sell"] = list(set(old_data["sell"]) ^ set(temp["sell"]))
    old_data["buy"] = list(set(old_data["buy"] + data["buy"]))
    old_data["sell"] = list(set(old_data["sell"] + data["sell"]))
    print(data["buy"])
    print(data["sell"])
    logger.info("Stocks - buy ")
    logger.info(data["buy"])
    if data["buy"]:
        tele = Tele(data["buy"])
        tele.send_message(f"Positive Ichimoku...")
    logger.info("Stocks - sell ")
    logger.info(data["sell"])
    if data["sell"]:
        tele = Tele(data["sell"])
        tele.send_message(f"Negative Ichimoku...")
    time.sleep(900.0 - (time.time() - start_time) % 900.0)
