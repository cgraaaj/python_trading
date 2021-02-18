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

url = "http://localhost:3000/strategies"
dri = Driver()

# LOCATE_PY_FILENAME = __file__
LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
# LOCATE_PY_PARENT_DIR = os.path.abspath(os.path.join(LOCATE_PY_DIRECTORY_PATH, ".."))

sectorkw = pd.read_csv(
    "{}/nsetools/sectorKeywords.csv".format(LOCATE_PY_DIRECTORY_PATH)
)
result = []
logfile = "{0}/logs/{1}.log".format(
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

strat_dict = dri.get_strategies()
for strat in strat_dict:
    logger.info("Running Strategy: {}".format(strat))
    sectorkw["Sector"].apply(
        lambda x: dri.run_strategy(
            sec=x, strategy=strat_dict[strat]["fun"], **strat_dict[strat]["kwargs"]
        )
    )
    strategy = Strategy(strat, dri.get_result())
    dri.set_result()
    logger.info("Strategy Result: {}".format(json.dumps(strategy.__dict__)))
    if len(strategy.sectors) > 0:
        result.append(strategy.__dict__)
data = {"date": datetime.now().strftime("%d-%m-%Y"), "strategy": result}
logger.info("Final data:{}".format(data))

resp = (
    requests.post(url, json=data)
    if requests.get("{}/{}".format(url, data["date"])).status_code != 200
    else requests.put("{}/{}".format(url, data["date"]), json=data)
)


logger.info("db response: {0}".format(resp.__dict__))