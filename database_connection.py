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
    commit_json_collection = json.load(file)

db = connect["Commit_DB"]
commit_collection = db["commit_collection"]
commit_collection.insert_many(commit_json_collection)

