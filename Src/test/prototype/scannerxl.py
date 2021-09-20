import asyncio
import xlwings as xw
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import pandas as pd
from datetime import datetime
import time as t

pd.set_option("display.width", 1500)
pd.set_option("display.max_columns", 75)
pd.set_option("display.max_rows", 5000)

api_id = 5931891
api_hash = "110492fc9d1d3225e0b1bd9a0b3d224c"
phone = "+919561218666"
username = "Rajvel Govindarajan"
excel_file = "/home/pudge/Desktop/PROJECTS/Python/trading/python_trading/scannerxl.csv"
wb = xw.Book(excel_file)

all_calls = "All Calls"
weekly = "WEEKLY stock selection +"
monthly = "MONTHLY stock selection +"
baladaily = "BALAStbuydaily-1"
balaweekly = "BALAStbuyweekly-2"
jkdiamond = "JK DIAMOND STOCK"
premom = "PREMIUM MOMENTUM STOCKS"
wpremom = "WEEKLY MOMENTUM STOCKS"

# premom_sheet = wb.sheets(premom)
all_sheet = wb.sheets(all_calls)
global client


async def test():
    client = TelegramClient(username, api_id, api_hash)
    await client.connect()
    # sent = await client.send_code_request(phone)
    await client.sign_in(phone)

    my_channel = await client.get_entity("https://t.me/joinchat/_4-LGGC132E4YTM1")
    offset_id = 0
    limit = 300
    all_messages = []
    total_messages = 0
    total_count_limit = 300
    dtfilter = "April 28, 2021"
    df = pd.DataFrame()
    while True:
        history = await client(
            GetHistoryRequest(
                peer=my_channel,
                offset_id=offset_id,
                offset_date=datetime.now(),
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0,
            )
        )
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
            result = message.message
            if result != None:
                msg = result.split("\n")
                if len(msg) == 3:
                    when = msg[1]
                    dt = when[when.index("When") + 6 : when.index("at") - 1]
                    timev = when[when.index("at") + 3 :]

                    data = msg[2]
                    data = data[data.index("Extra Data:") + 12 : data.index("@") - 1]
                    data = data.split(",")
                    signal = data[0]
                    for i in range(len(data) - 1):
                        if i == 0:
                            continue
                        sig = {}
                        sig["date"] = dt
                        sig["time"] = timev
                        sig["signal"] = signal
                        d = data[i].strip()
                        sig["symbol"] = d[: d.index(" - ")]
                        sig["price"] = d[d.index(" - ") + 3 :]
                        df = df.append([sig], ignore_index=True)

        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:

            condition = df["date"] == dtfilter
            filtered_df = df[condition]

            condition = filtered_df["signal"] == weekly
            weekly_df = filtered_df[condition]

            condition = filtered_df["signal"] == monthly
            monthly_df = filtered_df[condition]

            condition = filtered_df["signal"] == baladaily
            baladaily_df = filtered_df[condition]

            condition = filtered_df["signal"] == balaweekly
            balaweekly_df = filtered_df[condition]

            condition = filtered_df["signal"] == jkdiamond
            jkdiamond_df = filtered_df[condition]

            condition = filtered_df["signal"] == premom
            premom_df = filtered_df[condition]
            premom_df = premom_df.drop_duplicates(["time", "symbol", "price"])

            condition = filtered_df["signal"] == wpremom
            wpremom_df = filtered_df[condition]
            wpremom_df = wpremom_df.drop_duplicates(["time", "symbol", "price"])

            # weekly_sheet.range("A3").options(index=False,header=False).value = weekly_df.drop(["signal","date"],axis=1)
            # monthly_sheet.range("A3").options(index=False,header=False).value = monthly_df.drop(["signal","date"],axis=1)

            # bd_sheet.range("A3").options(index=False,header=False).value = baladaily_df.drop(["signal","date"],axis=1)
            # bw_sheet.range("A3").options(index=False,header=False).value = balaweekly_df.drop(["signal","date"],axis=1)
            # jkdiamond_sheet.range("A3").options(index=False,header=False).value = jkdiamond_df.drop(["signal","date"],axis=1)
            # premom_sheet.range("A3").options(index=False,header=False).value = premom_df.drop(["signal","date"],axis=1)
            all_sheet.range("A3").options(
                index=False, header=False
            ).value = jkdiamond_df.drop(["signal", "date"], axis=1)
            all_sheet.range("D3").options(
                index=False, header=False
            ).value = premom_df.drop(["signal", "date"], axis=1)
            all_sheet.range("G3").options(
                index=False, header=False
            ).value = wpremom_df.drop(["signal", "date"], axis=1)
            all_sheet.range("J3").options(
                index=False, header=False
            ).value = weekly_df.drop(["signal", "date"], axis=1)
            all_sheet.range("M3").options(
                index=False, header=False
            ).value = monthly_df.drop(["signal", "date"], axis=1)
            offset_id = 0
            all_messages = []

            df = pd.DataFrame()
            weekly_df = pd.DataFrame()
            monthly_df = pd.DataFrame()
            baladaily_df = pd.DataFrame()
            balaweekly_df = pd.DataFrame()
            jkdiamond_df = pd.DataFrame()
            premom_df = pd.DataFrame()
            wpremom_df = pd.DataFrame()
            t.sleep(5)

    await client.disconnect()


asyncio.run(test())
print("Client Created")
