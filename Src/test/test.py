import os
import sys

from utils.stoploss import atr
from nsetools.yahooFinance import YahooFinance as yf

# LOCATE_PY_FILENAME = __file__
# LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
# LOCATE_PY_PARENT_DIR = os.path.abspath(os.path.join(LOCATE_PY_DIRECTORY_PATH, ".."))
# print(LOCATE_PY_FILENAME)
# print(LOCATE_PY_DIRECTORY_PATH)
# print(LOCATE_PY_PARENT_DIR)

ticker = "CUB"
atr(yf(ticker + ".NS", result_range="7d", interval="1d").result)