import pandas as pd
import datetime as dt

from Src.nsetools.YahooFinance import YahooFinance as yf
from alpha_vantage.techindicators import TechIndicators


class Strategies:

    def __init__(self, nse):
        # alphaVantage key
        ti = TechIndicators(open('alphaVantage_key.txt', 'r').read())
        # BSE data
        # bseData = pd.read_csv('/home/pudge/Desktop/PROJECTS/Python/trading/test/source.csv')
        self.res = []
        self.today = dt.date.today()
        self.nse = nse;

    def get_seven_day_data_sma50(self, ticker='CUB'):

        sev_data = yf(ticker + '.NS', result_range='7d', interval='1d').result
        if sev_data.iloc[-1]['Close'] <= sev_data.iloc[0]['Close']:
            print('getting the data of {} 100days'.format(ticker))
            ticker_data = yf(ticker + '.NS', result_range='100d', interval='1d').result
            ticker_data['sma_50'] = ticker_data['Close'].rolling(window=50).mean()
            try:
                if ((ticker_data.iloc[-2]['sma_50'] > ticker_data.iloc[-2]['Close'] and ticker_data.iloc[-2][
                    'sma_50'] < (ticker_data.iloc[-2]['Close'] + (ticker_data.iloc[-2]['Close'] * .015)))
                        or (ticker_data.iloc[-2]['sma_50'] > (
                                ticker_data.iloc[-2]['Close'] + (ticker_data.iloc[-2]['Close'] * .015)) and
                            ticker_data.iloc[-2]['sma_50'] < ticker_data.iloc[-2]['Close'])):
                    print('--------------' + ticker + '--------------')
                    self.res.append(ticker)
            except:
                print('error occured....\n')

    def get_sma_slowFast(self, ticker='CUB', slow=200, fast=50):
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

    def run_in_sector(self, strategy, sec='Nifty 50', *args, **kwargs):
        print('XXXXXXXXXXXXXXX{}XXXXXXXXXXXXXXXX'.format(sec))
        stocks_of_sector = pd.DataFrame(self.nse.get_stocks_of_sector(sector=sec))
        stocks_of_sector['symbol'].apply(lambda x: strategy(**kwargs))
        # pd.DataFrame(list(set(res))).to_csv(sec+'.csv')

    def get_result(self):
        return self.res
    # get_sma_slowFast('VEDL',slow=100,fast=30)

    # get_sevenD_data()
    # data.columns=data.iloc[0]
    # data = data.loc[1:20]['SYMBOL']
    # data.apply(lambda x: get_sevenD_data(x))
    # data.apply(lambda x: print(x['SYMBOL']))
    # data = np.arange(start=0,stop=len(nse.get_stock_codes()),step=1)
    # data = len(nse.get_stock_codes())
    # pprint(data)
