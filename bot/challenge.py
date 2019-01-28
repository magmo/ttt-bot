from time import time
from firebase_admin import db
from bot.config import get_bot, K_ADDRESS, K_NAME, K_STAKE
from bot.util import str_to_hex

def get_now_ms():
    return int(time()*1000)

NOW = get_now_ms()

def _get_new_challenge(bot_addr):
    bot = get_bot(addr=bot_addr)
    return {
        'address': str_to_hex(bot[K_ADDRESS]),
        'name': bot[K_NAME],
        'isPublic': True,
        'stake': bot[K_STAKE],
        'createdAt': NOW
    }

def get_challenge_ref(bot_addr):
    return db.reference().child('challenges').child(str_to_hex(bot_addr))

def create_new_challenge(bot_addr):
    get_challenge_ref(bot_addr).set(_get_new_challenge(bot_addr))
