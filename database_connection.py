'''
Connessione al database MongoDB
'''
import json
import os

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Varaibile per attivare l'inserimento dei file nel DB
# Perché ho la 104 ed ho appena perso 10 minuti a capire perché nel DB ci fossero tante occorrenze con lo stesso commi_id -> perché ogni volta che avviavo lo script questo insieriva i duplicati
Populate_DB = False

try:
    localhost = "127.0.0.1"
    port = 27017
    client = MongoClient(host=localhost, port=port)
    print("MongoDB is reachable")
    print("DB -> " + str(client))
except ConnectionFailure as e:
    print("Could not connect to MongoDB")
    print(e)

# Path alla directory dei file
results_directory = "Results"

db = client["Revision_History_DB"]
# reference al database
collection = db["Revision_Collection"]
print("DB -> " + str(db))

if (Populate_DB):
    for results_commits_json in os.listdir(results_directory):
        path_file_in_dir = os.path.join(results_directory, results_commits_json)
        print("File_Name: " + results_commits_json + "  ---  File_Path: " + path_file_in_dir)

        # inserimento dei file nel DB
        with open(path_file_in_dir) as json_file:
            iters_json = json.load(json_file)
            collection.insert_many(iters_json)

# Questa query ritorna solamente il nome di tutti i file che sono non leggibili della prima commit
# cursor = collection.find_one({"revision_history": {"$elemMatch": {"isReadable": False}}}, {"revision_history.file_name": 1})


'''
Funzione che ritorna tutti i file unredable di un determianto commit
- La query ritorna solamente il nome del file
'''
def find_only_unreadable_file_byCommitID(commit_id):
    cursor = collection.find_one({"revision_history":
                                      {"$elemMatch": {"isReadable": False}},
                                  "commit_id": commit_id},
                                 {"revision_history.file_name": 1})

    for i in cursor['revision_history']:
        print(i)

'''
La Funzione restituisce gli Id delle commit ed il timestamp di tutte le occorrenze del file in cui risulta unredable 
'''
def find_file_NotReadable_occurence(file_name):

    cursor = collection.find({"revision_history":
                                  {"$elemMatch": {"$and": [{"file_name": file_name}, {"isReadable": False}]}},
                              "revision_history.file_name": file_name},
                             {"commit_id": 1, "timestamp": 1})

    for file_occurence in cursor:
        print("Commit: " + file_occurence['commit_id'] + "  ||  Timestamp: " + file_occurence['timestamp'])

    #if((len(list(cursor))) == 0):
    #    print("The file [" + file_name + "] is always readable")
    #else:
    #    for file_occurence in cursor:
    #        print(file_occurence)
            # print("Commit: " + file_occurence['commit_id'] + "  ||  Timestamp: " + file_occurence['timestamp'] + "  ||  isReadable: " + file_occurence['isReadable'])



'''
Funzione per stampare i valori delle query
- Stampe in base al caso
S: Standard - Solo print
'''


def print_cursor(cursor, print_type):
    if (print_type == "S"):
        print(cursor)
    else:
        print("Print Error")

find_only_unreadable_file_byCommitID("bd2b0a632bfc5aabb408e7f47cfaa52a7d1b2b50")
#find_file_NotReadable_occurence("modules/elasticsearch/src/main/java/org/elasticsearch/action/bulk/TransportShardBulkAction.java")