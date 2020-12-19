from Src.Strategies import Strategies
import pandas as pd
import os
from Src.nsetools.nse import Nse
from pprint import pprint

nse = Nse()
st = Strategies(nse=nse)

data= pd.DataFrame(list(nse.get_stock_codes().items()))
sectorkw = pd.read_csv(os.getcwd()+'/nsetools/sectorKeywords.csv')
sectorkw.iloc[7:]['Sector'].apply(lambda x:st.runInSector(sec=x,strategy=st.get_sma_slowFast,ticker='MRF',slow=100,fast=30))
print('00000000000000000000000  FINAL   000000000000000000000')
pprint(set(st.get_result()))