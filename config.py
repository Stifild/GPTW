import os, json
from dotenv import load_dotenv


load_dotenv()

LOGS_PATH = ".\data\logs.log"
DB_NAME = ".\data\database.db"
DB_TABLE_USERS_NAME = "users"

FOLDER_ID = os.getenv('FOLDER_ID')

GPT_MODEL = "yandexgpt-lite"
MAX_ONTASK_TOKENS = 50
TEMPERATURE = 0.6
ADMIN_LIST = [6303315695]

IAM_TOKEN_ENDPOINT = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
IAM_TOKEN_PATH = "data/token_data.json"
TOKENS_DATA_PATH = "data/tokens_count.json"