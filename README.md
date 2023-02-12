# ElasticSearch Analysis

- [ElasticSearch Analysis](#elasticsearch-analysis)
  - [Introduction](#introduction)
  - [Methodology](#methodology)
  - [Test replication](#test-replication)
    - [Requirements](#requirements)
    - [How to create the dataset](#how-to-create-the-dataset)
    - [How to run the analysis](#how-to-run-the-analysis)
  - [References](#references)

## Introduction

This repository was created to analyze the history of the Elasticsearch project.

The goal was to go in search of the **5 Java classes that have been unreadable for the longest time** and the **10 developers who have introduced the most unreadable classes** into the project.

## Methodology

The methodology used for our tests was as follows:

Once we downloaded the Git repository of the affected code (in our case Elasticsearch), to get the complete history of the project, starting from the first commit, we used the following command:

`git log --reverse --pretty=format:"%H|%an|%at"`

Once executed we will get in output a list of strings that will be composed in the following way:

```text
...
<commit_hash>|<author_name>|<commit_timestamp>
...
```

Once this was done, from each commit, all the file names that were changed in that specific commit were extracted using the following command:

`git show --name-only --pretty=format:\"\" <commit_hash>`

Finally, for each of the extracted files, the readability score was calculated using the following [tool](https://dibt.unimol.it/report/readability/).

The tool returns a value between 0 and 1 that goes to indicate the probability that the class is readable.

| Value           | Meaning    |
| --------------- | ---------- |
| 0 <= x < 0.4    | Unreadable |
| 0.4 <= x <= 0.6 | Unsure*    |
| 0.6 < x <= 1    | Readable   |

---

***Unsure\***: This term is used to indicate that you are not sure whether the class is readable or not*

---

Then a JSON file was created containing all the results of the analysis (of course, before the file was analyzed, the commit was moved to get the correct status of the file using the command `git checkout <commit_hash>`)

We then proceeded to insert all this data within MongoDB, so that we could conveniently create queries that would allow us to extract the analyzed data.

For this very reason, queries were created that allowed us to obtain:

- **5 Java classes that have been unreadable for the longest time**
- **10 developers who have introduced the most unreadable classes**

## Test replication

In case you would like to replicate the study, you can find the dataset used from the following [link](https://www.kaggle.com/datasets/djalba/elasticsearch-history).

While as for the tool you can download it from this [link](https://dibt.unimol.it/report/readability/files/readability.zip)

### Requirements

- Python 3.6+
- Java 8+
- Docker
- Docker Compose

### How to create the dataset

In case you want to create a new dataset to work on, you can proceed as follows:

- Clone the repository.

    ```bash
    git clone https://github.com/dj-d/elasticsearch-analysis.git

    cd elasticsearch-analysis
    ```

- Clone the Elasticsearch project.

    ```bash
    git clone https://github.com/elastic/elasticsearch.git
    ```

- Create a virtual environment and install dependencies.

    ```bash
    # Create virtual environment
    python3 -m venv venv

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

- Create a file named `.env` in the main folder of this project and add the following environment variables.

    ```env
    PROJECT_PATH=/main/path/of/the/project/to/analyze/
    TOOL_PATH=/main/path/of/the/tool/to/be/used/

    START_COMMIT=0 # Start commit index
    END_COMMIT=100 # End commit index

    FILES_LOCATION=/path/where/to/save/the/generated/files
    OUTPUT_JSON_NAME=file_name.json
    ```

    Note that, the tool used in our experiments, is also present within our repository, so you will not need to download it, but just add the path within the `.env` file

---

***Note**: I have no idea what to do on **winzoz**, I have not tested it, so "**Long live Linux**"*

---

- Now you can run the script.

    ```bash
    python main.py
    ```

### How to run the analysis

To perform the tests, you must proceed using the following instructions:

- Download the dataset from the following [link](https://www.kaggle.com/datasets/djalba/elasticsearch-history) (unless it was created in the [previous step](#how-to-create-the-dataset)).
- Now you need to add a new environment variable (you can add it either to an existing .env file or in a new one in case it is missing)

    ```env
    ...
    PATH_ARCHIVE=/path/to/the/downloaded/dataset

    MONGODB_ROOT_PASSWORD=ROOT_PASSWORD
    MONGODB_USERNAME=USER_NAME
    MONGODB_PASSWORD=USER_PASSWORD
    ...
    ```

- Now you need to start the MongoDB container.

    ```bash
    docker-compose up -d
    ```

- Now you can run the analysis.

    ```bash
    python database_connection.py
    ```

- Once the script has completed its execution, within the root directory of this project, there will be two .csv files with the results of the analysis.

## References

- [Git - git-log Documentation](https://git-scm.com/docs/pretty-formats)