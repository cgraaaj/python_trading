import pandas as pd
import os
import sys
import json
import logging
import requests

from strategy import Strategy
from driver import Driver
from datetime import datetime
from pprint import pprint

url = 'http://localhost:3000/strategies'
dri = Driver()
sectorkw = pd.read_csv('/home/pi/Trading/python_trading/Src/nsetools/sectorKeywords.csv')
result = []
logfile = "/home/pi/Trading/python_trading/Src/logs/"+datetime.now().strftime("%d-%m-%Y")+".log"

if not os.path.exists(logfile):
    open(logfile, 'a').close()

logging.basicConfig(
    filename=logfile,
    format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m-%d %H:%M:%S',
    level=logging.INFO,
    filemode='w'
    )
logger = logging.getLogger(__name__)

strat_dict = dri.get_strategies()
for strat in strat_dict:
    logger.info("Running Strategy: "+strat)
    sectorkw['Sector'][7:9].apply(lambda x:dri.run_strategy(sec=x,strategy=strat_dict[strat]['fun'],**strat_dict[strat]['kwargs']))
    strategy = Strategy(strat,dri.get_result())
    dri.set_result()
    logger.info("Result: "+json.dumps(strategy.__dict__))
    result.append(strategy.__dict__)
data = {
    'date': datetime.now().strftime("%d-%m-%Y"),
    'strategy': result
}

response = requests.post(url,json=data)

logger.info("db response: {0}".format(response.json()))