from pymongo import MongoClient

mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)
db = client['SuperZol']
products_collection = db["products"]
super_markets_collection = db["superMarkets"]
