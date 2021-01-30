from pymongo import MongoClient

class Mongodb:
    def __init__(self):
        client = MongoClient('mongodb+srv://velan_mongodb:Raju6713@cluster0.64cqd.mongodb.net/trading?retryWrites=true&w=majority')
        self.db= client['trading']
        self.col=self.db.get_collection('strategy')
    
    def get_collection(self):
        return self.col

    def get_db(self):
        return self.db