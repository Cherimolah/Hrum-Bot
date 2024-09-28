import os

from dotenv import load_dotenv

load_dotenv()


API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

ENTRY_TIMEOUT = os.getenv('ENTRY_TIMEOUT')
ENTRY_TIMEOUT = tuple(map(int, ENTRY_TIMEOUT[1:-1].split(',')))
