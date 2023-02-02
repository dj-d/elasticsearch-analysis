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
    connect = MongoClient(host=localhost, port=port)
    print("MongoDB is reachable")
    print(connect)
except ConnectionFailure as e:
    print("Could not connect to MongoDB")
    print(e)

#Path alla directory dei file
results_directory = "Results"


db = connect["Revision_History_DB"]
commit_collection = db["Revision_Collection"]

for results_commits_json in os.listdir(results_directory):
    path_file_in_dir = os.path.join(results_directory, results_commits_json)
    print("File_Name: " + results_commits_json + "  ---  File_Path: " + path_file_in_dir)

    with open(path_file_in_dir) as json_file:
        iters_json = json.load(json_file)
        commit_collection.insert_many(iters_json)


    #TODO: Vedi come si fanno le query



#Trovo i file da inserire
# with open("fileJSONProva.json") as file:
#    revision_history = json.load(file)

#Creo il database
#db = connect["Revision_History_DB"]
#commit_collection = db["Revision_Collection"]


#commit_collection.insert_many(revision_history)

