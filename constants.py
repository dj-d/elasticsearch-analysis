import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_PATH=os.getenv('PROJECT_PATH', default=None)
TOOL_PATH=os.getenv('TOOL_PATH', default=None)

START_COMMIT = int(os.getenv('START_COMMIT', default=0))
END_COMMIT = int(os.getenv('END_COMMIT', default=10))

FILES_LOCATION = os.getenv('FILES_LOCATION', default=None)
OUTPUT_JSON_NAME = os.getenv('OUTPUT_JSON_NAME', default='output.json')
