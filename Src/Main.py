from strategies import Strategies
import pandas as pd
import os
from nsetools.nse import Nse
from nsetools.yahooFinance import YahooFinance as yf
from pprint import pprint

nse = Nse()
st = Strategies(nse=nse)

data = pd.DataFrame(list(nse.get_stock_codes().items()))
sectorkw = pd.read_csv(os.getcwd()+'/Src/nsetools/sectorKeywords.csv')
sectorkw['Sector'][:7].apply(lambda x:st.run_in_sector(sec=x,strategy=st.support_sma))
# print(st.get_seven_day_data_sma50())
print('00000000000000000000000   FINAL   000000000000000000000')
pprint(st.get_result())

# data = yf('COFORGE' + '.NS', result_range='1mo', interval='1d').result
# pprint(data)