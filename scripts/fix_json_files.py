"""
This script goes to fix the problem on the "isReadable" field when an error code is present and goes to add the "isUnsure" field
"""
import os
import json

# The folder where the json files are located
INPUT_FOLDER_PATH = '/home/dj-d/Downloads/Results/'

# The folder where the new json files will be located
OUTPUT_FOLDER_PATH = '/home/dj-d/Downloads/Fixed/'

files = os.listdir(INPUT_FOLDER_PATH)

if len(files) != 0:
    for file in files:
        with(open(f'{INPUT_FOLDER_PATH}{file}', 'r')) as f:
            data = json.load(f)

        for sub_data in data:
            if len(sub_data['revision_history']) != 0:
                for index, revision in enumerate(sub_data['revision_history']):

                    if revision['score'] >= 0 and revision['score'] < 0.4:
                        revision['isReadable'] = False
                        revision['isUnsure'] = False
                    elif revision['score'] > 0.6 and revision['score'] <= 1:
                        revision['isReadable'] = True
                        revision['isUnsure'] = False
                    else:
                        revision['isReadable'] = False
                        revision['isUnsure'] = True

        with(open(f'{OUTPUT_FOLDER_PATH}{file}', 'w')) as f:
            json.dump(data, f, indent=4)
    
    print('Done!')
else:
    print('No files found!')