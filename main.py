import os
import subprocess
import json

PROJECT_PATH='/home/dj-d/Repositories/GitHub/elasticsearch/'
TOOL_PATH='/home/dj-d/University/Automated_Software_Delivery/Exam/readability'

def get_hisoty(project_path: str) -> list:
    os.chdir(project_path)

    cmd = f'git log --reverse --pretty=format:"%H|%an|%at"'

    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _output, _error = process.communicate()

    if len(_error) > 0:
        print(f'_error: {_error.decode("utf-8")}')

        exit(1)
        
    commit_list = [sub.replace('\n', '') for sub in _output.decode('utf-8').split('\"')]
    no_empty = [x for x in commit_list if x != '']
    
    return no_empty

def get_commit_files(commit: str) -> list:
    """
    Get the files of a commit

    :param commit: the commit to be analyzed (hash)

    :return: the list of files of the commit
    """

    os.chdir(PROJECT_PATH)
    cmd = f'git show --name-only --pretty=format:\"\" {commit}'

    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _output, _error = process.communicate()

    if len(_error) > 0:
        print(f'_error: {_error.decode("utf-8")}')
        exit(1)

    file_list = [x for x in _output.decode('utf-8').split()[1:] if x.endswith('.java')]

    return file_list

def get_score(file_path: str) -> dict:
    """
    Get the score of a file

    :param file_path: path of the file to be analyzed

    :return: the score of the file
    """

    if not file_path.endswith('.java'):
        print('File is not a java file')
        # exit(0)
        return {'error': 'File is not a java file', 'code': -2.0, 'score': -1.0}
    
    if not os.path.isfile(PROJECT_PATH + file_path):
        print('File does not exist')
        # exit(0)
        return {'error': 'File does not exist', 'code': -3.0, 'score': -1.0}

    os.chdir(TOOL_PATH)
    cmd = f'java -jar rsm.jar {PROJECT_PATH}{file_path}'
    process = subprocess.Popen(
        cmd.split(), 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
        )
    
    _output, _error = process.communicate()

    if len(_error) > 0:
        print(f'_error: {_error.decode("utf-8")}')
        # exit(1)
        return {'error': f'_error: {_error.decode("utf-8")}', 'code': -4.0, 'score': -1.0}

    score = _output.decode('utf-8').split()[-1]

    if score == 'NaN':
        score = -1.0
    
    if len(score) <= 0:
        print('Score error')
        # exit(2)
        return {'error': 'Score error', 'code': -5.0, 'score': -1.0}

    return {'error': '', 'code': 0.0, 'score': float(score)}

def checkout(to: str) -> None:
    """
    Checkout to a commit

    :param to: the commit to be checked out (hash)

    :return: None
    """

    os.chdir(PROJECT_PATH)
    cmd = f'git -c advice.detachedHead=false checkout {to}'

    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _output, _error = process.communicate()

    if len(_error) > 0:
        print(f'_error: {_error.decode("utf-8")}')
    
    print(f'checkout_output: {_output.decode("utf-8")}')

if __name__ == "__main__":
    checkout(to="main")

    history = get_hisoty(project_path=PROJECT_PATH)

    history_file = open('/home/dj-d/Repositories/GitHub/asd_exam/history.txt', 'w')
    history_file.write('\n'.join(history))
    history_file.close()

    data = list()
    
    START_COMMIT = 0
    END_COMMIT = 100

    for line in history[START_COMMIT:END_COMMIT + 1]:
        line = line.strip().split('|')
        commit = line[0]
        author_name = line[1]
        timestamp = line[2]

        print(f'Commit: {commit}')
        
        main_body = {
            'commit_id': commit, 
            'author_name': author_name,
            'timestamp': timestamp,
            'revision_history': list()
            }

        files = get_commit_files(commit=commit)

        checkout(to=commit)
        
        if len(files) > 0:
            for file in files:
                print(f'File: {file}')

                rsm = get_score(file_path=file)

                print(f"Score['code']: {rsm['code']}, Score['score']: {rsm['score']}")

                main_body['revision_history'].append({
                        'file_name': file,
                        'score': rsm['score'],
                        'isReadable': True if rsm['score'] > 0.6 else False,
                        'error': rsm['error'],
                        'code': rsm['code']
                    })

        data.append(main_body)

    with open("/home/dj-d/Repositories/GitHub/asd_exam/iter1.json", "w") as write_file:
        json.dump(data, write_file, indent=4)
