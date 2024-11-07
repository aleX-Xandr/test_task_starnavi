from os import environ, path

from dotenv import load_dotenv

load_dotenv()
PROJECT_DIR = path.dirname(path.abspath(__file__))
CONFIG_FILE = environ.get("APP_CONFIG_FILE")
PAGINATION_SIZE = 100
