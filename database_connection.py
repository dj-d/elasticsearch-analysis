import csv
from _operator import itemgetter

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

from constants import MONGODB_ROOT_PASSWORD

'''
- GLOBAL VARIABLES
@data_file_list: The list of all files with readability and time values to analyze
@interval_files_dict: A dictionary where the key is the file_name and the value is an integer expressing the minutes of unreadability
'''
data_file_list = []
interval_files_dict = {}

try:
    user = "root"
    password = MONGODB_ROOT_PASSWORD
    host = "0.0.0.0"
    port = 27017
    client = MongoClient(f"mongodb://{user}:{password}@{host}:{port}")
    print("MongoDB is reachable")
    print("DB -> " + str(client))
except ConnectionFailure as e:
    print("Could not connect to MongoDB")
    print(e)

# Database
db = client["revision_history_db"]
collection = db["revision_history_collection"]
print("DB -> " + str(db))

def get_all_commit_in_DB():
    """
    :return: the list of commit ids in the Database
    """
    cursor = collection.find({}, {"commit_id": 1})
    for i in cursor:
        print(i["commit_id"])
    return list(cursor)


def get_all_file():
    """
    :return List of all readable and unreadable files in the DB
    """
    cursor = collection.find({}, {"revision_history.file_name": 1, "_id": 0})
    unique_file_names = set()

    for commit_files in cursor:
        for file in commit_files['revision_history']:
            unique_file_names.add(file['file_name'])

    print("Total Files: " + str(len(unique_file_names)))
    return unique_file_names


def get_all_unreadable_file():
    '''
    :return List of all files that are unreadable therefore the files in the DB that have
            at least a score lower than 0.4 in a commit
    '''

    cursor = collection.aggregate([
        {'$unwind': '$revision_history'},
        {'$match': {'revision_history.score': {"$gte": 0, "$lt": 0.4}}}
    ])

    unique_unreadable_file_names = set()

    for noteReadable_file in cursor:
        unique_unreadable_file_names.add(noteReadable_file['revision_history']['file_name'])

    print("Unreadable Files: " + str(len(unique_unreadable_file_names)))
    return unique_unreadable_file_names


def get_file_timestamps_and_readable(file_name):
    """
    The function takes a file as input, returns the timestamps of the commits in which it is present and whether it is readable or not.
    :param file_name the name of the file of which we want to obtain the relative times and readability
    :return dictionary with the listed values of timestamps, readability and commit_id related to readability
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
    @param: initial and final timestamp
    @return: the interval that divides the two dates in minutes (float)
    '''
    delta_seconds = int(second_timestamp) - int(first_timestamp)
    delta_minutes = delta_seconds / 60
    # print("Delta: " + str(delta_minutes))
    return delta_minutes


def get_most_unreadable():
    # get the unreadable files in the DB
    print("Find all commits files...")
    all_unreadable_file_set = get_all_unreadable_file()

    for analyzed_file_index, file in enumerate(all_unreadable_file_set):
        print("Analyzing: (" + str(analyzed_file_index + 1) + "/" + str(len(all_unreadable_file_set)) + ") -> " + str(
            file))
        # get the values [timestamp, readabilty and commit_ids] of the input file
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
                        # case: only one element in the array
                        second_timestamp = 0
                    else:
                        if file_details['readability'][index - 1] == True or file_details['unsure'][index - 1] == True:
                            # case: last false of array with previous True. No range is counted.
                            second_timestamp = 0
                        else:
                            second_timestamp = file_details['timestamp'][index]
                            interval_files_dict[str(file)] += get_minutes_delta(first_timestamp=first_timestamp,
                                                                                second_timestamp=second_timestamp)


                elif first_timestamp == 0:
                    # case: First case
                    first_timestamp = file_details['timestamp'][index]
                    interval_files_dict[str(file)] += 0
                    only_one = True

                else:
                    # case: intermediate false does not add
                    second_timestamp = file_details['timestamp'][index]
                    only_one = False
            elif (file_details['readability'][index] == False) and (file_details['unsure'][index] == True):
                if file_details['unsure'][
                    index - 1] == False and only_one == False and index != 0 and first_timestamp != 0:
                    # case: uncertain and therefore we need to take the previous one and calculate
                    second_timestamp = file_details['timestamp'][index - 1]
                    interval_files_dict[str(file)] += get_minutes_delta(first_timestamp=first_timestamp,
                                                                        second_timestamp=second_timestamp)
                    first_timestamp = 0
                    second_timestamp = 0
                elif only_one == True:
                    # case: just one false and unsure True
                    second_timestamp = file_details['timestamp'][index]
                    interval_files_dict[str(file)] += get_minutes_delta(first_timestamp=first_timestamp,
                                                                        second_timestamp=second_timestamp)
                    only_one = False
                    first_timestamp = 0
                    second_timestamp = 0
            elif (file_details['readability'][index] == True) and (file_details['unsure'][index] == False):
                if only_one == True:
                    # case: only one false and unreadable True
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
    :param  l'ID of one commit
    :return the name of the commit Author
    """
    cursor = collection.find_one({"commit_id": str(commit_id)}, {"_id": 0, "author_name": 1})

    return cursor['author_name']


def get_all_authors():
    """
    :return: List without duplicates of all the authors present in the DB
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
    :return the function assigns to authors who introduce unreadable files
            an integer representing the number of unreadable files introduced in the whole project
    """

    authors_dict = {}
    print("\n" + "Get Most unreadable Authors...")
    for dict_file in data_file_list:
        for index in range(len(dict_file['readabilities_file'])):
            '''
            This check is necessary because we only need the authors of files that are unreadable.
            So both isUnsure and isREadable need to be FASLE.
            '''
            if ((dict_file['readabilities_file'][index] == False) and (dict_file['unsure'][index]) == False):
                authors = get_Commit_Author(commit_id=dict_file['commit_id_file'][index])
                if authors in authors_dict:
                    authors_dict[authors] = authors_dict[authors] + 1
                else:
                    authors_dict[authors] = 1
                # Break the iterating on the first appearance of the False value in a file's readability
                break

    # List of authors sorted in descending order to find the 10
    authors_dict = sorted(authors_dict.items(), key=lambda x: x[1], reverse=True)

    print("Author_DIC_Length: " + str(len(authors_dict)))
    print("\n")

    with open("output_authors.csv", "w", newline="", encoding="utf-8") as file_auth:
        writer_auth = csv.writer(file_auth)
        for index, author in enumerate(authors_dict):
            print(str(index) + " - " + str(author[0]) + " : " + str(author[1]))
            writer_auth.writerow([author[0], author[1]])


get_most_unreadable()
get_most_unreadable_author()
