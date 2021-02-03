import os
import sys
sys.path.append(os.path.realpath('..'))

from data.mongodb import Mongodb

db = Mongodb()
doc = db.get_collection().find({})
for d in doc:
    for item in d:
        print(item)