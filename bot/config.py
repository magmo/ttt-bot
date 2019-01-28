from collections import OrderedDict
from os import environ

PROJ_DEV = 'rock-paper-scissors-dev'
def get_project():
    return environ.get('GOOGLE_CLOUD_PROJECT', PROJ_DEV)

ENV_PROD = 'env_prod'
ENV_DEV = 'env_dev'
def get_env():
    return ENV_DEV if get_project() == PROJ_DEV else ENV_PROD

if get_env() == ENV_DEV:
    from bot.config_dev import ADDRESSES, NAMES, WALLET_UID, PKS
else:
    from bot.config_prod import ADDRESSES, NAMES, WALLET_UID, PKS

ROPSTEN = 'ropsten'
KOVAN = 'kovan'
TESTNET = ROPSTEN

FINNEY = int(1e15)
STAKES_IN_FUNDING = 5
NUM_BOTS = 4

NUM_MOVES = 3
K_ADDRESS = 'bot_addr'
K_NAME = 'bot_name'
K_WALLET_UID = 'bot_wallet_uid'
K_PK = 'bot_pk'
K_STAKE = 'bot_stake'

_BOTS = OrderedDict()

def create_bots():
    for i_bot in range(0, NUM_BOTS):
        bot = {}
        bot[K_ADDRESS] = ADDRESSES[i_bot]
        bot[K_NAME] = NAMES[i_bot]
        bot[K_WALLET_UID] = WALLET_UID[i_bot]
        bot[K_PK] = PKS[i_bot]
        bot[K_STAKE] = FINNEY
        _BOTS[ADDRESSES[i_bot]] = bot

def get_bot(addr=None, index=0):
    if not _BOTS:
        create_bots()

    if addr:
        return _BOTS[addr]
    return list(_BOTS.values())[index]

def get_bot_addr(index=0):
    return get_bot(index=index)[K_ADDRESS]
