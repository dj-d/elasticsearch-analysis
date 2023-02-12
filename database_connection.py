'''
Connessione al database MongoDB
'''
import json
import os
from _operator import itemgetter

import pymongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
import csv

# Varaibile per attivare l'inserimento dei file nel DB
# Perché ho la 104 ed ho appena perso 10 minuti a capire perché nel DB ci fossero tante occorrenze con lo stesso commi_id -> perché ogni volta che avviavo lo script questo insieriva i duplicati
Populate_DB = False

# creo il dizionario globale
data_file_list = []
interval_files_dict = {}

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
# results_directory = "Results_Test"

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


def get_all_commit_in_DB():
    """
    :return: la lista degli id dei commit presenti nel Database
    """
    cursor = collection.find({}, {"commit_id": 1})

    for i in cursor:
        print(i["commit_id"])

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

    # for index, file in enumerate(unique_unreadable_file_names):
    #    print(str(file) + "\n")

    print("File illegibili: " + str(len(unique_unreadable_file_names)))
    return unique_unreadable_file_names


def get_file_timestamps_and_readable(file_name):
    """
    .$ elemento di proiezione
    La funzione preso in input un file, ritorna i timestamp delle commit in cui è presente e se risuta readable o no.
    :param file_name il nome del file del quale vogliamo ottenre i timestemps e la leggibilità relativa
    :return dizionario key:value  commit_timestamp : isReadable_value
    """
    pipeline = [
        {"$match": {"revision_history.file_name": file_name}},
        {"$unwind": "$revision_history"},
        {"$match": {"revision_history.file_name": file_name}},
        {"$project": {
            "timestamp": 1,
            "commit_id": 1,
            "isUnsure": "$revision_history.isUnsure",
            "isReadable": "$revision_history.isReadable"
        }}, {"$sort": {"timestamp": 1}}
    ]
    cursor = collection.aggregate(pipeline)

    readability = list()
    timestamp = list()
    commit_id = list()
    unsure = list()

    for file_occurrence in cursor:
        readability.append(bool(file_occurrence['isReadable']))
        unsure.append(bool(file_occurrence['isUnsure']))
        timestamp.append(str(file_occurrence['timestamp']))
        commit_id.append(str(file_occurrence['commit_id']))

    return {"timestamp": timestamp, "readability": readability, "unsure": unsure, "commit_id": commit_id}


def get_minutes_delta(first_timestamp, second_timestamp):
    '''
    @param: timestamp iniziale e timestamp finale
    @return: l'intervallo che divide le due date in minuti (float)
    '''
    delta_seconds = int(second_timestamp) - int(first_timestamp)
    delta_minutes = delta_seconds / 60
    # print("Delta: " + str(delta_minutes))
    return delta_minutes


def get_most_unreadable():
    # prende solo i file illegibili nel DB
    print("Find all commits files...")
    all_unreadable_file_set = get_all_unreadable_file()

    for analyzed_file_index, file in enumerate(all_unreadable_file_set):
        print("Analyzing: (" + str(analyzed_file_index + 1) + "/" + str(len(all_unreadable_file_set)) + ") -> " + str(file))
        # otteniamo i valori del file analizzato
        file_details = get_file_timestamps_and_readable(str(file))

        # popolare la lista con i dizionari
        data_file_list.append(
            {
                "name_file": str(file),
                "timestamps_file": file_details['timestamp'],
                "readabilities_file": file_details['readability'],
                "unsure": file_details['unsure'],
                "commit_id_file": file_details['commit_id']
            }
        )
        # check on file_details length
        if (len(file_details['timestamp']) != len(file_details['readability']) or (
                len(file_details['readability']) != (len(file_details['commit_id'])))):
            print("Error in dict array lenght - Function: data_file_dict")
            raise

        first_timestamp = 0
        second_timestamp = 0
        only_one = False
        interval_files_dict[str(file)] = 0
        for index in range(len(file_details['readability'])):
            if (file_details['readability'][index] == False) and (file_details['unsure'][index] == False):
                if index == (len(file_details['readability']) - 1):
                    if len(file_details['readability']) == 1:
                        # caso di un solo elemento nell'array
                        second_timestamp = 0
                    else:
                        if file_details['readability'][index - 1] == True or file_details['unsure'][index - 1] == True:
                            # caso ultimo false dell'array con precedenti True non si conta intervallo
                            second_timestamp = 0
                        else:
                            second_timestamp = file_details['timestamp'][index]
                            interval_files_dict[str(file)] += get_minutes_delta(first_timestamp=first_timestamp,
                                                                                second_timestamp=second_timestamp)


                elif first_timestamp == 0:
                    # primo caso
                    first_timestamp = file_details['timestamp'][index]
                    interval_files_dict[str(file)] += 0
                    only_one = True

                else:
                    # false intermedio non si aggiunge
                    second_timestamp = file_details['timestamp'][index]
                    only_one = False
            elif (file_details['readability'][index] == False) and (file_details['unsure'][index] == True):
                if file_details['unsure'][
                    index - 1] == False and only_one == False and index != 0 and first_timestamp != 0:
                    # caso in cui siamo incerti e quindi bisogna prendere il precendente e calcoliamo
                    second_timestamp = file_details['timestamp'][index - 1]
                    interval_files_dict[str(file)] += get_minutes_delta(first_timestamp=first_timestamp,
                                                                        second_timestamp=second_timestamp)
                    first_timestamp = 0
                    second_timestamp = 0
                elif only_one == True:
                    # caso solo un false ed unsure True
                    second_timestamp = file_details['timestamp'][index]
                    interval_files_dict[str(file)] += get_minutes_delta(first_timestamp=first_timestamp,
                                                                        second_timestamp=second_timestamp)
                    only_one = False
                    first_timestamp = 0
                    second_timestamp = 0
            elif (file_details['readability'][index] == True) and (file_details['unsure'][index] == False):
                if only_one == True:
                    # Solo un false ed unreadable True
                    second_timestamp = file_details['timestamp'][index]
                    interval_files_dict[str(file)] += get_minutes_delta(first_timestamp=first_timestamp,
                                                                        second_timestamp=second_timestamp)
                    only_one = False
                    first_timestamp = 0
                    second_timestamp = 0

    sorted_files_deltaTime = sorted(interval_files_dict.items(), key=itemgetter(1), reverse=True)

    with open("output_files.csv", "w", newline="") as file:
        writer = csv.writer(file)
        for time in sorted_files_deltaTime:
            writer.writerow([time[0], time[1]])


def get_Commit_Author(commit_id):
    """
    :param  l'ID di una commit
    :return il nome dell'autore della commit
    """
    cursor = collection.find_one({"commit_id": str(commit_id)}, {"_id": 0, "author_name": 1})

    return cursor['author_name']


def get_all_authors():
    """

    :return: la lista senza duplicati di tutti gli autori presenti nel DB
    """
    cursor = collection.find({}, {"_id": 0, "author_name": 1})

    authors_set = set()
    for author in cursor:
        authors_set.add(author['author_name'])
        # print(author['author_name'])

    for index, author in enumerate(authors_set):
        print(str(index) + " -> " + author)


def get_most_unreadable_author():
    """
    :param
    :return la funzione assegna agli autori che introducono file illegibili un intero che rappresenta il numero di file non leggibili introdotti in tutto il progetto
    """

    authors_dict = {}
    print("\n" + "Get Most unreadable Authors...")
    for dict_file in data_file_list:
        for index in range(len(dict_file['readabilities_file'])):
            '''
            Questo controllo è necessario perché ci servono solamente gli autori dei file che sono illegibli 
            sicuramente. Quindi sia isUnsure che isREadable sono false. 
            '''
            if ((dict_file['readabilities_file'][index] == False) and (dict_file['unsure'][index]) == False):
                authors = get_Commit_Author(commit_id=dict_file['commit_id_file'][index])
                if authors in authors_dict:
                    authors_dict[authors] = authors_dict[authors] + 1
                else:
                    authors_dict[authors] = 1
                # Break the iterating on the first appearance of the False value in a file's readability
                break

    # Lista degli autori ordinata decrescentemente per trovare i 10
    authors_dict = sorted(authors_dict.items(), key=lambda x: x[1], reverse=True)

    # Stampa il dizionario degli autori con le occorrenze
    print("Author_DIC_Length: " + str(len(authors_dict)))
    print("\n")

    with open("output_authors.csv", "w", newline="", encoding="utf-8") as file_auth:
        writer_auth = csv.writer(file_auth)
        for index, author in enumerate(authors_dict):
            print(str(index) + " - " + str(author[0]) + " : " + str(author[1]))
            writer_auth.writerow([author[0], author[1]])


get_most_unreadable()
get_most_unreadable_author()
