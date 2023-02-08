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


def find_only_unreadable_file_byCommitID(commit_id):
    """
    :param  l'id di una commit
    :return tutti i file unredable di un determianto commit, la query ritorna solamente il nome del file
    """

    cursor = collection.find_one({"revision_history":
                                      {"$elemMatch": {"isReadable": False}},
                                  "commit_id": commit_id},
                                 {"revision_history.file_name": 1})

    for i in cursor['revision_history']:
        print(i)


def find_file_NotReadable_occurrence(file_name):
    """
    :return Id delle commit ed il timestamp di tutte le occorrenze del file in cui risulta unredable
    """
    cursor = collection.find({"revision_history":
                                  {"$elemMatch": {"$and": [{"file_name": file_name}, {"isReadable": False}]}},
                              "revision_history.file_name": file_name},
                             {"commit_id": 1, "timestamp": 1})

    i = 1
    for file_occurence in cursor:
        print(str(i) + " ->" + "File not Readable in Commit: " + file_occurence['commit_id'] + "  ||  Timestamp: " +
              file_occurence['timestamp'])
        i = i + 1

    # if((len(list(cursor))) == 0):
    #    print("The file [" + file_name + "] is always readable")
    # else:
    #    for file_occurence in cursor:
    #        print(file_occurence)
    # print("Commit: " + file_occurence['commit_id'] + "  ||  Timestamp: " + file_occurence['timestamp'] + "  ||  isReadable: " + file_occurence['isReadable'])


def get_all_commit_in_DB():
    """
    :return: la lista degli id dei commit presenti nel Database
    """
    cursor = collection.find({}, {"commit_id": 1})
    index = 1
    for i in cursor:
        print(str(index) + " -> " + i["commit_id"])
        index = index + 1

    return list(cursor)


def get_all_file():
    """
    La funzione restituisce tutti i file presenti nel database
    Per farlo utilizza la struttura set() che non può contenere duplicati
    dunque ogni file occorre una sola volta

    :return  Lista di tutti i file presenti nel DB
    """
    cursor = collection.find({}, {"revision_history.file_name": 1, "_id": 0})

    # Set per inserire i nomi di file unici
    # Set non può contenere duplicati
    unique_file_names = set()

    for commit_files in cursor:
        for file in commit_files['revision_history']:
            unique_file_names.add(file['file_name'])

    # stampa la lista dei file
    for file in unique_file_names:
        print(file)

    print("Total Files: " + str(len(unique_file_names)))

    return unique_file_names


def get_all_unreadable_file():
    '''
    :return la lista di tutti i file che risultano unreadable quindi i file nel DB che hanno almeno uno score inferiore a 0.4 in una commit
    '''

    cursor = collection.aggregate([
        {'$unwind': '$revision_history'},
        {'$match': {'revision_history.score': {"$gte": 0, "$lt": 0.4}}}
    ])

    # Set per inserire i nomi di file unici
    # Set non può contenere duplicati
    unique_unreadable_file_names = set()

    z = 1
    for noteReadable_file in cursor:
        # print(str(z) + ":" + str(noteReadable_file['revision_history']['file_name']) + "\n")
        unique_unreadable_file_names.add(noteReadable_file['revision_history']['file_name'])

    for index, file in enumerate(unique_unreadable_file_names):
        print(str(file) + "\n")

    print(len(unique_unreadable_file_names))
    return unique_unreadable_file_names


def get_file_timestamps(file_name):
    """
    :param file_name il nome del file del quale vogliamo ottenre i timestemps
    :return la lista dei timestamp dato un file in input
    """
    cursor = collection.find({"revision_history.file_name": file_name}, {"timestamp": 1, "_id": 0})
    i = 1

    for file_occurrence in cursor:
        print(str(i) + " -> " + str(file_occurrence))
        i = i + 1

    return list(cursor)


def get_file_timestamps_and_readable(file_name):
    """
    .$ elemento di proiezione
    La funzione preso in input un file, ritorna i timestamp delle commit in cui è presente e se risuta readable o no.
    :param file_name il nome del file del quale vogliamo ottenre i timestemps e la leggibilità relativa
    :return dizionario key:value  commit_timestamp : isReadable_value
    """
    cursor = collection.find({"revision_history.file_name": file_name},
                             {"timestamp": 1, "_id": 0, "revision_history.isReadable.$": 1}
                             )
    i = 1
    # dizionario
    file_Timestemps_Readability_dictionary = {}
    for file_occurrence in cursor:
        # Get Readable and Timestamp value
        file_commit_isReadable = str(file_occurrence["revision_history"][0]['isReadable'])
        file_commit_timestamp = str(file_occurrence["timestamp"])
        file_Timestemps_Readability_dictionary[file_commit_timestamp] = file_commit_isReadable

        # print(str(i) + " -> " + str(file_occurrence))
        # i = i + 1
    # print dizionario
    # for value in file_Timestemps_Readability_dictionary:
    #     print(value + " : " + file_Timestemps_Readability_dictionary[value])

    return file_Timestemps_Readability_dictionary


def data_file_dict(name_file, timestamps_file, readabilities_file):
    """
    La funzione ritorna un dizionario cone le informazioni da analizzare
    :param

    :return
    """

    data_files_dict = {}
    data_files_dict['name_file'] = name_file
    data_files_dict['timestamps_file'] = timestamps_file
    data_files_dict['readabilities_file'] = readabilities_file
    if len(data_files_dict['timestamps_file']) != len(data_files_dict['readabilities_file']):
        print("Error in dict array lenght - Function: data_file_dict")
        raise
    else:
        return data_files_dict


def get_most_unreadable():
    # creo il dizionario
    data_file_list = []
    # prende solo i file illegibili nel DB
    all_unreadable_file_set = get_all_unreadable_file()

    for file in all_unreadable_file_set:
        # print("# - - File Name: " + str(file))
        # otteniamo i valori del file analizzato
        file_details = get_file_timestamps_and_readable(str(file))
        # popolare la lista con i dizionari
        data_file_list.append(data_file_dict(name_file=str(file),
                                             timestamps_file=list(file_details.keys()),
                                             readabilities_file=list(file_details.values())
                                             )
                              )
    # print all
    for index in data_file_list:
        print(index)


# find_only_unreadable_file_byCommitID("bd2b0a632bfc5aabb408e7f47cfaa52a7d1b2b50")
# find_file_NotReadable_occurence("modules/elasticsearch/src/main/java/org/elasticsearch/action/bulk/TransportShardBulkAction.java")
# get_all_commit_in_DB()
# get_all_file()
# get_all_file_timestamps("modules/benchmark/micro/src/main/java/org/elasticsearch/benchmark/index/engine/SimpleEngineBenchmark.java")
# A = "modules/elasticsearch/src/main/java/org/elasticsearch/index/merge/policy/LogByteSizeMergePolicyProvider.java"
# get_all_file_timestamps_and_readable(A)
# find_file_NotReadable_occurrence(A)
# get_all_unreadable_file()
get_most_unreadable()
# get_all_file()