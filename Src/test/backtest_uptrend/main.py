import sys
import pandas as pd
import datetime
pd.options.mode.chained_assignment = None
sys.path.insert(1, "/home/pudge/Trading/python_trading/Src")
from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse
from driver import Driver
import time

arr = [1,2,3,4,5]
n=4
res = [arr[i:i+n] for i in range(4)]
dri = Driver()
nse = Nse()

master={}

def isUpTrend(data):
    data["uptrend"] = (data["Close"] > data["Close"].shift(1)) & (
        data["Close"] > data["Open"]
    )
    if (data["uptrend"].values.sum() == data.shape[0] - 1):
        return True
    return False

def trade(ticker_data):
    profit_index = None
    loss_index = None
    bought_at = ticker_data.iloc[0]["Open"]
    stop_loss = bought_at - (bought_at*0.005)
    print(stop_loss)
    stop_profit = bought_at + (bought_at*0.01)
    print(stop_profit)
    ticker_data = ticker_data.iloc[3:]
    ticker_data["Profit"] = ticker_data["Close"] >= stop_profit
    ticker_data["Loss"] = ticker_data["Close"] <= stop_loss
    # print(ticker_data[ticker_data["Profit"]])
    if not ticker_data[ticker_data["Profit"]].empty:
        profit_index = ticker_data[ticker_data["Profit"]].index[0]
    # print(ticker_data[ticker_data["Loss"]])
    if not ticker_data[ticker_data["Loss"]].empty:
        loss_index = ticker_data[ticker_data["Loss"]].index[0]
    if loss_index and profit_index == None:
        sold_at = ticker_data.loc[loss_index]["Close"]
        print(f"loss at {loss_index} with {sold_at-bought_at}")
        return [f'{stock} {str(loss_index)}',bought_at,sold_at,sold_at-bought_at]
    elif profit_index and loss_index == None:
        sold_at = ticker_data.loc[profit_index]["Close"]
        print(f"profit at {profit_index} with {sold_at-bought_at}")
        return [f'{stock} {str(profit_index)}',bought_at,sold_at,sold_at-bought_at]
    elif profit_index < loss_index:
        sold_at = ticker_data.loc[profit_index]["Close"]
        print(f"profit at {profit_index} with {sold_at-bought_at}")
        return [f'{stock} {str(profit_index)}',bought_at,sold_at,sold_at-bought_at]
    else:
        sold_at = ticker_data.loc[loss_index]["Close"]
        print(f"loss at {loss_index} with {sold_at-bought_at}")
        return [f'{stock} {str(loss_index)}',bought_at,sold_at,sold_at-bought_at]

def check_data(stock, ticker_data, rnge):
    if ticker_data.shape[0] != rnge:
        time.sleep(120)
        print(f"checking again {stock}")
        get_pl_stock(stock)

def get_pl_stock(stock):
    print(f'checking for {stock}')
    rnge = 21
    data = []
    master_data = dri.get_ticker_data(
            ticker=stock, range=str(rnge) + "d", interval="1d"
        )
    check_data(stock, master_data, rnge)
    ticker_datas = [master_data.iloc[i:i+n] for i in range(18)]
    # print(ticker_datas[len(ticker_datas)-1])
    for ticker_data in ticker_datas:
        if isUpTrend(ticker_data):
            trend_day_loc = master_data.index.get_loc(ticker_data.index[-1])
            try:
                trade_day = master_data.index[trend_day_loc+1]
                next_day = trade_day.to_pydatetime() + datetime.timedelta(days=1)
                trade_day = trade_day.to_pydatetime().strftime("%d-%m-%Y")
                next_day = next_day.strftime("%d-%m-%Y")
                ticker_data = yf(ticker=stock, start=trade_day,end=next_day, interval="1m").result
                # print(ticker_data)
                data.append(trade(ticker_data))
            except:
                print(master_data.index[trend_day_loc])
    df = pd.DataFrame(data,columns=['T_day','Buy','Sell','PL'])
    # df.set_index('T_day',inplace=True)
    if not df.empty:
        print(df)
        master[stock] = df

sectors = pd.read_csv(
    "/home/pudge/Trading/python_trading/Src/nsetools/sectorKeywords.csv"
)
for sec in sectors["Sector"].tail(1):
    # for sec in sectors.loc[5:17,"Sector"]:
    # for sec in sectors:
    print(sec)
    stocks_of_sector = pd.DataFrame(nse.get_stocks_of_sector(sector=sec))
    stocks_of_sector["symbol"] = stocks_of_sector["symbol"].apply(lambda x: x + ".NS")
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     executor.map(get_uptrend, stocks_of_sector["symbol"])
    for stock in stocks_of_sector["symbol"]:
        get_pl_stock(stock)

frames = [df for df in master.values()]
result = pd.concat(frames)
print(result)
result.set_index("T_day",inplace=True)
result.to_csv("out.csv")
print(f"Total pl is {result['PL'].sum()}")