import pandas as pd
import sys
from driver import Driver
from telegram_helper import Tele

dri = Driver()
trade = sys.argv[1]
marketcap_BTCs_INR = "BTC-INR,ETH-INR,BNB-INR,XRP-INR,USDT-INR,ADA-INR,DOGE-INR,DOT1-INR,UNI3-INR,LTC-INR,LINK-INR,BCH-INR,THETA-INR,XLM-INR,FIL-INR,USDC-INR,VET-INR,TRX-INR,EOS-INR,SOL1-INR,BSV-INR,MIOTA-INR,LUNA1-INR,CRO-INR"
ticker_btc_monitor = [
    {"ticker": "BTC-INR", "brk_out": 232000.00},
    {"ticker": "ETH-INR", "brk_out": 138000.00},
    {"ticker": "BNB-INR", "brk_out": 20400.00},
    {"ticker": "DOGE-INR", "brk_out": 13.1},
]
# 13.1
ticker_equity_monitor = [
    {"ticker": "TRIDENT.NS", "brk_out": 20.00},
    {"ticker": "ADANIPOWER", "brk_out": 75.00},
    # {"ticker": "BNB-INR", "brk_out": 20400.00},
    # {"ticker": "DOGE-INR", "brk_out": 13.10},
]


ticker_to_monitor = ticker_btc_monitor if trade == "bitcoin" else ticker_equity_monitor
for ticker_dict in ticker_to_monitor:
    ticker_data = dri.get_ticker_data(
        ticker=ticker_dict["ticker"], range=str(1) + "d", interval="1d"
    )
    if ticker_data["Close"][0] <= ticker_dict["brk_out"]:
        fname = "myid"
        message = f'{ticker_dict["ticker"]} has broke {ticker_dict["brk_out"]}'
        tele = Tele(message, chat_ids_fname=fname)
        tele.send_message("-----Breakout Alert-----")
