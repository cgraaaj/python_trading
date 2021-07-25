import telegram
import os
from dotenv import load_dotenv
import concurrent.futures
import multiprocessing


class Tele:
    def __init__(self, message,chat_ids_fname):
        self.message = message
        LOCATE_PY_DIRECTORY_PATH = os.path.abspath(os.path.dirname(__file__))
        load_dotenv("{}/.env".format(LOCATE_PY_DIRECTORY_PATH))
        file1 = open("{}/data/{}.txt".format(LOCATE_PY_DIRECTORY_PATH,chat_ids_fname), "r")
        self.bot = telegram.Bot(token=os.getenv("STOCK_BOT_TOKEN"))
        self.chat_ids = file1.readlines()

    def send(self, id, message):
        self.bot.sendMessage(chat_id=id, text=message)
        if isinstance(self.message, str):
            self.bot.sendMessage(chat_id=id, text=self.message)
        elif isinstance(self.message, list):
            for content in self.message:
                if isinstance(content, dict):
                    self.bot.sendMessage(
                        chat_id=id, text=f'{content["name"]} - {content["volume"]}'
                    )
                else:
                    self.bot.sendMessage(chat_id=id, text=f"{content}")
        else:
            print(self.message)

    def send_message(self, message):
        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     executor.map(self.send, self.chat_ids)
        processes = []
        for id in self.chat_ids:
            p = multiprocessing.Process(target=self.send, args=[id, message])
            p.start()
            processes.append(p)
        for pros in processes:
            pros.join()
