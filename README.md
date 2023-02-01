# ElasticSearch Analysis

<!-- TODO: Added project description -->

## How to use

Create a virtual environment and install dependencies.

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a file named `.env` in the main folder of this project and add the following environment variables.

```env
PROJECT_PATH=/main/path/of/the/project/to/analyze/
TOOL_PATH=/main/path/of/the/tool/to/be/used/

START_COMMIT=0 # Start commit index
END_COMMIT=100 # End commit index

FILES_LOCATION=/path/where/to/save/the/generated/files
OUTPUT_JSON_NAME=file_name.json
```

---

***Note**: i have no idea what to do on **winzoz** for environment variables, so "**Long live Linux**"*

---

Now you can run the script.

```bash
python main.py
```

### References

- [Git - git-log Documentation](https://git-scm.com/docs/pretty-formats)