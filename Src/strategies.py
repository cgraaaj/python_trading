import pandas as pd
import datetime as dt
import logging

from dateutil.relativedelta import relativedelta
from nsetools.yahooFinance import YahooFinance as yf
from nsetools.nse import Nse
# from alpha_vantage.techindicators import TechIndicators


logging.basicConfig(
    filename="logs/"+dt.datetime.now().strftime("%d-%m-%Y")+".log",
    format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m-%d %H:%M:%S',
    level=logging.INFO,
    filemode='w'
)
logger = logging.getLogger(__name__)

class Strategies:
    def __init__(self):
        # alphaVantage key
        # ti = TechIndicators(open('Src/alphaVantage_key.txt', 'r').read())
        # BSE data
        # bseData = pd.read_csv('/home/pudge/Desktop/PROJECTS/Python/trading/test/source.csv')
        self.res = []
        self.dict_sector= {}
        self.exception = []
        self.today = dt.date.today()
        self.nse = Nse()
        self.strategies = {'Slow fast SMA':{'fun':self.get_sma_slowFast,'kwargs':{'slow':100,'fast':30}},'Seven Day SMA50':{'fun':self.get_seven_day_data_sma50,'kwargs':{}}}
        # self.strategies = {'Seven Day SMA50':{'fun':self.get_seven_day_data_sma50,'kwargs':{}}}

    # returns the indices which has ltp near to sma50 in last 7days
    def get_seven_day_data_sma50(self, ticker='CUB'):
        # logger.info("Stock :"+ticker)
        sev_data = yf(ticker + '.NS', result_range='7d', interval='1d').result
        if sev_data.iloc[-1]['Close'] <= sev_data.iloc[0]['Close']:
            ticker_data = yf(ticker + '.NS', result_range='100d', interval='1d').result
            ticker_data['sma_50'] = ticker_data['Close'].rolling(window=50).mean()
            if(len(ticker_data.index)>1):
                if ((ticker_data.iloc[-2]['sma_50'] > ticker_data.iloc[-2]['Close'] 
                     and ticker_data.iloc[-2]['sma_50'] < (ticker_data.iloc[-2]['Close'] + (ticker_data.iloc[-2]['Close'] * .015)))
                        or (ticker_data.iloc[-2]['sma_50'] > (ticker_data.iloc[-2]['Close'] + (ticker_data.iloc[-2]['Close'] * .015))
                            and ticker_data.iloc[-2]['sma_50'] < ticker_data.iloc[-2]['Close'])
                        ):
                    self.res.append(ticker)
            else:
                self.exception.append(ticker)
            
    # returns the index of whose fastSMA cuts its slowSMA in last 4 days
    def get_sma_slowFast(self, ticker='CUB', slow=200, fast=50):
        # logger.info("Stock :"+ticker)
        ticker_data = yf(ticker + '.NS', result_range=str((slow * 2)) + 'd', interval='1d').result
        ticker_data['sma_fast'] = ticker_data.iloc[(slow * 2) - (fast * 2):]['Close'].rolling(window=fast).mean()
        ticker_data['sma_slow'] = ticker_data['Close'].rolling(window=slow).mean()
        ticker_data['sma_diff'] = ticker_data['sma_slow'] - ticker_data['sma_fast']
        data = ticker_data[ticker_data['sma_diff'] <= (ticker_data['sma_slow'] * 0.005)]
        if (len(data) >= 1):
            data = data.index[0]
            if ticker_data.iloc[ticker_data.index.get_loc(data)].name > self.today - dt.timedelta(days=4):
                print('FOUND in {}--------------'.format(ticker))
                self.res.append(ticker)
                print(ticker_data.iloc[ticker_data.index.get_loc(data)].name)

    # returns the index for which the price will fall on (or) above the sma within last 40 days
    def support_sma(self, ticker='CUB', support=50):
        months = 3
        ticker_data = yf(ticker+'.NS', result_range=str((months*30)+support)+'d',interval='1d').result
        ticker_data['sma'] = ticker_data['Close'].iloc[50:].rolling(window=support).mean()
        ticker_data = ticker_data[ticker_data['sma']>1]
        sma_diff = (ticker_data['Close'] > ticker_data['sma']) & (ticker_data['Close'] < (ticker_data['sma'] + (ticker_data['Close']*0.05)))
        res = ticker_data[sma_diff].index.date > self.today-relativedelta(months=2)
        if (len(res)>30):
            self.res.append(ticker)

    # loops through the sectors for indices
    def run_strategy(self, strategy, sec='Nifty 50', *args, **kwargs):
        # print('XXXXXXXXXXXXXXX{}XXXXXXXXXXXXXXXX'.format(sec))
        logger.info("Sector: "+sec)
        stocks_of_sector = pd.DataFrame(self.nse.get_stocks_of_sector(sector=sec))
        stocks_of_sector['symbol'].apply(lambda x: strategy(**kwargs,ticker=x))
        self.dict_sector[sec]=self.res
        self.res=[]
        
        
    # returns result and exception if any
    def get_result(self):
        # return {'stocks':list(set(self.res)),'excep':list(set(self.exception))}
        return self.dict_sector

    def set_result(self):
        # return {'stocks':list(set(self.res)),'excep':list(set(self.exception))}
         self.dict_sector={}    
    
    # returns available strategies
    def get_strategies(self):
        return self.strategies