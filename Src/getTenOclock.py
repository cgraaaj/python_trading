import os
import json
import concurrent.futures
import telegram
import time

from driver import Driver
from datetime import datetime
from pprint import pprint
import time

start_time = time.time()
LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))

dri = Driver()
res = {}
bot = telegram.Bot(token="1667958437:AAHD9dnq51iuNeZDPa9gDhtJSCSTza4thto")


def send_stocks(id):
    bot.sendMessage(chat_id=id, text="Alert, These stocks broke days high...")
    for stock in res["stocks"]:
        bot.sendMessage(chat_id=id, text=stock)


def getStocks():
    dri.run_strategy(sec="FO Stocks", strategy=dri.days_high_break)

    res["time"] = datetime.now().strftime("%H:%M:%S")
    res["stocks"] = list(dri.get_result()[0]["stocks"])

    file1 = open("{}/data/chat_ids.txt".format(LOCATE_PY_DIRECTORY_PATH), "r")
    chat_ids = file1.readlines()

    # processes = []
    # for id in chat_ids:
    #     p = multiprocessing.Process(target=send_stocks, args=[id, res["stocks"]])
    #     p.start()
    #     processes.append(p)
    # for pros in processes:
    #     pros.join()
    if len(res["stocks"]) > 0:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            executor.map(send_stocks, chat_ids)
        # results = [executor.submit(send_stocks, id, res["stocks"]) for id in chat_ids]
        # to get results of that function
        # for f in concurrent.futures.as_completed(results):
        #     print(f.result())

        with open("/home/pi/telegramBOT/stock_bot/data/data.json", "a") as outfile:
            outfile.write("\n")
            json.dump(res, outfile)
        print("--- %s seconds ---" % (time.time() - start_time))


dri.run_strategy(sec="FO Stocks", strategy=dri.days_high)
time.sleep(60 * 4)
# print(dri.tests())
# from 10:15 to 3:30
t_end = time.time() + 60 * ((5 * 60) + 15)
while time.time() < t_end:
    getStocks()
    time.sleep(300.0 - (time.time() - start_time) % 300)