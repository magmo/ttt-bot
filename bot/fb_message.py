from firebase_admin import db
from bot import coder
from bot.util import str_to_hex
from bot.wallet import sign_message

K_MESSAGES = 'messages'


def _get_addr_ref(addr):
    return db.reference().child(K_MESSAGES).child(str_to_hex(addr))


def message_consumed(key, addr):
    _get_addr_ref(addr).child(key).delete()


def message_opponent(message, bot_addr):
    state_type = coder.get_channel_state(message)
    queue = 'GAME_ENGINE'
    # Postfund and conclusion messages are sent to the wallet
    if state_type == 1 or state_type == 3:
        queue = 'WALLET'
    hex_message = str_to_hex(message)
    signature = str_to_hex(sign_message(hex_message, bot_addr))

    d_message = {
        'data': hex_message,
        'signature': signature,
        'queue': queue
    }

    players = coder.get_channel_players(message)
    opponents = list(filter(lambda player: player != bot_addr, players))
    opponent_address = opponents[0]
    ref = _get_addr_ref(opponent_address)
    ref.push(d_message)
