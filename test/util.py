import json

from bot.config import ADDRESSES
from bot.util import str_to_hex

def get_wallets_fn(f_json):
    def get_wallets(_):
        with open(f'test/fb_data/{f_json}.json', 'r') as f_wallets:
            return json.load(f_wallets)
    return get_wallets

def get_bot0_addr():
    return str_to_hex(ADDRESSES[0])
