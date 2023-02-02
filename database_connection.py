'''
Connessione al database MongoDB
'''
import json
import os

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


try:
    localhost = "127.0.0.1"
    port = 27017
    client = MongoClient(host=localhost, port=port)
    print("MongoDB is reachable")
    print("DB -> " + str(client))
except ConnectionFailure as e:
    print("Could not connect to MongoDB")
    print(e)

#Path alla directory dei file
results_directory = "Results"


db = client["Revision_History_DB"]
# reference al database
collection = db["Revision_Collection"]
print("DB -> " + str(db))

for results_commits_json in os.listdir(results_directory):
    path_file_in_dir = os.path.join(results_directory, results_commits_json)
    print("File_Name: " + results_commits_json + "  ---  File_Path: " + path_file_in_dir)

    #inserimento dei file nel DB
    with open(path_file_in_dir) as json_file:
        iters_json = json.load(json_file)
        collection.insert_many(iters_json)


cursor = collection.find_one({"revision_history.isReadable": bool(False)})

print(cursor)


