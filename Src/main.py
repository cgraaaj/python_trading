import pandas as pd
import os
# import sys
import json
import logging

from strategies import Strategies
from data.mongodb import Mongodb
# from flask import Flask,jsonify
# from flask_restful import Api, Resource
from datetime import datetime
# from nsetools.yahooFinance import YahooFinance as yf
from pprint import pprint

logfile = "logs/"+datetime.now().strftime("%d-%m-%Y")+".log"

if not os.path.exists(logfile):
    open(logfile, 'a').close()

logging.basicConfig(
    filename=logfile,
    format='[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%m-%d %H:%M:%S',
    level=logging.INFO,
    filemode='w'
    )
logger = logging.getLogger(__name__)
# app = Flask(__name__)
# api = Api(app)
st = Strategies()
db = Mongodb()

sectorkw = pd.read_csv(os.getcwd()+'/nsetools/sectorKeywords.csv')

# #Test API with one Strategy
# class Test(Resource):
#     def get(self, sector):
#         # data = pd.DataFrame(list(nse.get_stock_codes().items()))
        
#         rng = sector.split(':')
#         if(len(rng)==2):
#             frm = rng[0]
#             to = rng[1]
#             sectorkw['Sector'][int(frm):int(to)].apply(lambda x:st.run_in_sector(sec=x,strategy=st.get_seven_day_data_sma50))
#         else:
#             st.run_in_sector(sec=sector,strategy=st.get_seven_day_data_sma50)
#         return{'data':st.get_result()}

# #Runs Strategies available in every sectors
# class Strat(Resource):
#     def get(self):
#         result = {}
#         strat_dict = st.get_strategies()
#         for strat in strat_dict:
#             logger.info("Running Strategy: "+strat)
#             sectorkw['Sector'][7:9].apply(lambda x:st.run_strategy(sec=x,strategy=strat_dict[strat]['fun'],**strat_dict[strat]['kwargs']))
#             result[strat]=st.get_result()
#             st.set_result()
#             logger.info("Result: "+json.dumps(result))
#         res_json = json.loads('{\"'+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+'\":'+json.dumps(result)+'}')
#         db.get_collection().insert(res_json)
#         return json.loads('{\"'+datetime.now().strftime("%d/%m/%Y %H:%M:%S")+'\":'+json.dumps(result)+'}')

# api.add_resource(Test,'/test/<string:sector>')
# api.add_resource(Strat,'/strat')

# if __name__ == "__main__":
#     app.run(debug=True)


result = {}
strat_dict = st.get_strategies()
for strat in strat_dict:
    logger.info("Running Strategy: "+strat)
    sectorkw['Sector'].apply(lambda x:st.run_strategy(sec=x,strategy=strat_dict[strat]['fun'],**strat_dict[strat]['kwargs']))
    result[strat]=st.get_result()
    st.set_result()
    logger.info("Result: "+json.dumps(result))
res_json = json.loads('{\"'+datetime.now().strftime("%d-%m-%Y")+'\":'+json.dumps(result)+'}')

db.get_collection().insert_one(res_json)