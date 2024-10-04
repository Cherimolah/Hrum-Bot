import os

from dotenv import load_dotenv

load_dotenv()


API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

ENTRY_TIMEOUT = os.getenv('ENTRY_TIMEOUT')
if ENTRY_TIMEOUT is not None:
    ENTRY_TIMEOUT = tuple(map(int, ENTRY_TIMEOUT[1:-1].split(',')))
else:
    ENTRY_TIMEOUT = (3600, 7200)
AUTO_CLAIM_DAILY_REWARD = os.getenv('AUTO_CLAIM_DAILY_REWARD')
if AUTO_CLAIM_DAILY_REWARD is None or AUTO_CLAIM_DAILY_REWARD == 'True':
    AUTO_CLAIM_DAILY_REWARD = True
else:
    AUTO_CLAIM_DAILY_REWARD = False
