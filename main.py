import os
import subprocess

PROJECT_PATH='/home/dj-d/Repositories/GitHub/elasticsearch/'
TOOL_PATH='/home/dj-d/University/Automated_Software_Delivery/Exam/readability'

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

    return _output.decode('utf-8').split()[1:]

def get_score(file_path: str) -> str:
    """
    Get the score of a file

    :param file_path: path of the file to be analyzed
    
    :return: the score of the file
    """

    if not file_path.endswith('.java'):
        print('File is not a java file')
        exit(0)
    
    if not os.path.isfile(file_path):
        print('File does not exist')
        exit(0)

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
        exit(1)

    score = _output.decode('utf-8').split()[-1]

    if score == 'NaN':
        score = '-1'
    
    if len(score) <= 0:
        print('Score error')
        exit(2)

    return score

if __name__ == "__main__":
    print(get_score('test/test-clusters/src/main/java/org/elasticsearch/test/cluster/local/LocalClusterFactory.java'))