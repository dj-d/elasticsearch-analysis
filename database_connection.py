'''
Connessione al database MongoDB
'''
import json

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


try:
    localhost = "127.0.0.1"
    port = 27017
    connect = MongoClient(host=localhost, port=port)
    print("MongoDB is reachable")
    print(connect)
except ConnectionFailure as e:
    print("Could not connect to MongoDB")
    print(e)

with open("fileJSONProva.json") as file:
    revision_history = json.load(file)

db = connect["Revision_History_DB"]
commit_collection = db["Revision_Collection"]
commit_collection.insert_many(revision_history)

