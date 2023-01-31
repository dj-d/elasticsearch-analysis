import os
import subprocess
import json

from constants import PROJECT_PATH, TOOL_PATH, START_COMMIT, END_COMMIT, FILES_LOCATION, OUTPUT_JSON_NAME


def get_hisoty(project_path: str) -> list:
    """
    Get the revision history of the project from the first commit to the last

    :param project_path: the path of the project

    :return: the history of the project
    """
    
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

def get_commit_files(project_path: str, commit: str) -> list:
    """
    Get the changed files of a commit

    :param project_path: the path of the project
    :param commit: the commit to be analyzed (hash)

    :return: the list of files of the commit
    """

    os.chdir(project_path)
    cmd = f'git show --name-only --pretty=format:\"\" {commit}'

    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _output, _error = process.communicate()

    if len(_error) > 0:
        print(f'_error: {_error.decode("utf-8")}')
        exit(1)

    file_list = [x for x in _output.decode('utf-8').split()[1:] if x.endswith('.java')]

    return file_list

def get_score(project_path: str, file_path: str, tool_path: str) -> dict:
    """
    Get the score of a file about readability

    :param project_path: the path of the project
    :param file_path: path of the file to be analyzed
    :param tool_path: path of the tool

    :return: the score of the file
    """

    if not file_path.endswith('.java'):
        print('File is not a java file')
        # exit(0)
        return {'error': 'File is not a java file', 'code': -2.0, 'score': -1.0}
    
    if not os.path.isfile(project_path + file_path):
        print('File does not exist')
        # exit(0)
        return {'error': 'File does not exist', 'code': -3.0, 'score': -1.0}

    os.chdir(tool_path)
    cmd = f'java -jar rsm.jar {project_path}{file_path}'
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
    
    return {'error': '', 'code': 0.0, 'score': float(score)}

def checkout(project_path: str, to: str) -> None:
    """
    Checkout to a commit

    :param project_path: the path of the project
    :param to: the commit to be checked out (hash)

    :return: None
    """

    os.chdir(project_path)
    cmd = f'git -c advice.detachedHead=false checkout {to}'

    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    _output, _error = process.communicate()

    if len(_error) > 0:
        print(f'_error: {_error.decode("utf-8")}')
    
    print(f'checkout_output: {_output.decode("utf-8")}')

def stash(project_path: str) -> None:
    """
    Stash the changes

    :param project_path: the path of the project

    :return: None
    """

    os.chdir(project_path)
    os.system('git stash')

if __name__ == "__main__":
    if START_COMMIT == 0 or not os.path.exists(f'{FILES_LOCATION}/history.txt'):
        checkout(
            project_path=PROJECT_PATH,
            to="main"
            )

        history = get_hisoty(
            project_path=PROJECT_PATH
            )

        history_file = open(f'{FILES_LOCATION}/history.txt', 'w')
        history_file.write('\n'.join(history))
        history_file.close()
    else:
        history_file = open(f'{FILES_LOCATION}/history.txt', 'r')
        history = history_file.readlines()
        history_file.close()

    data = list()
    
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

        files = get_commit_files(
            project_path=PROJECT_PATH,
            commit=commit
            )

        checkout(
            project_path=PROJECT_PATH,
            to=commit
            )
        
        if len(files) > 0:
            for file in files:
                print(f'File: {file}')

                rsm = get_score(
                    project_path=PROJECT_PATH,
                    file_path=file,
                    tool_path=TOOL_PATH
                    )

                print(f"Score['code']: {rsm['code']}, Score['score']: {rsm['score']}")

                main_body['revision_history'].append({
                        'file_name': file,
                        'score': rsm['score'],
                        'isReadable': True if rsm['score'] > 0.6 else False,
                        'error': rsm['error'],
                        'code': rsm['code']
                    })

        data.append(main_body)

    with open(f"{FILES_LOCATION}/{OUTPUT_JSON_NAME}", "w") as write_file:
        json.dump(data, write_file, indent=4)
