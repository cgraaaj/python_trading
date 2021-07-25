import telegram
import os
from dotenv import load_dotenv
import sys

sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")

class Tele:
    def __init__(self, chat_ids_fname, data_path):
        LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..'))
        load_dotenv("{}/.env".format(LOCATE_PY_DIRECTORY_PATH))
        file1 = open("{}/data/{}.txt".format(LOCATE_PY_DIRECTORY_PATH,chat_ids_fname), "r")
        self.bot = telegram.Bot(token=os.getenv("STOCK_BOT_TOKEN"))
        self.chat_ids = file1.readlines()
        self.data_path = data_path

    def send(self):
        for chat_id in self.chat_ids:
            for file in os.listdir(self.data_path):
                self.bot.sendDocument(chat_id=chat_id, document=open(f'{self.data_path}/{file}', 'rb'))