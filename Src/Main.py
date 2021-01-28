from strategies import Strategies
import pandas as pd
import os
import sys
import json
from nsetools.nse import Nse
from nsetools.yahooFinance import YahooFinance as yf
from pprint import pprint

nse = Nse()
st = Strategies(nse=nse)

#sector = 'Nifty 50'
data = pd.DataFrame(list(nse.get_stock_codes().items()))
sectorkw = pd.read_csv(os.getcwd()+'/Src/nsetools/sectorKeywords.csv')
#To run in range
# sectorkw['Sector'].apply(lambda x:st.run_in_sector(sec=x,strategy=st.get_seven_day_data_sma50))
#To run in single sector
# print(st.get_seven_day_data_sma50())
st.run_in_sector(sec=sys.argv[1],strategy=st.get_seven_day_data_sma50)
# print('00000000000000000000000   FINAL   000000000000000000000')
print(json.dumps(st.get_result()))
sys.stdout.flush()

# data = yf('COFORGE' + '.NS', result_range='1mo', interval='1d').result
# pprint(data)