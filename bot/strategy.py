from random import randint
from web3 import Web3

from bot.coder import get_game_precommit
from bot.config import ADDRESSES, NUM_MOVES
from bot.external import reverse_hash_fail
from bot.util import hex_to_str, str_to_hex


ROCK = 0

# Error definitions
class StrategyError(Exception):
    pass

class InvalidStrategyError(StrategyError):
    def __str__(self):
        return 'The strategy does not exist'

def _raise_error():
    raise InvalidStrategyError()

def _incremental_move(move):
    return (move + 1) % NUM_MOVES

def _pick_rock(_last_bot_move, _last_opponent_move, _hex_message):
    return ROCK

def _pick_increment(last_bot_move, _last_opponent_move, _hex_message):
    if last_bot_move is None:
        return ROCK
    return _incremental_move(last_bot_move)

def _pick_opponent_increment(_last_bot_move, last_opponent_move, _hex_message):
    if last_opponent_move is None:
        return randint(ROCK, NUM_MOVES)
    return _incremental_move(last_opponent_move)

def _decode_move(hex_message):
    move_hash = get_game_precommit(hex_message)
    salt = "".join(['4' for i in range(0, 64)])
    hex_salt = str_to_hex(salt)

    for move in range(ROCK, NUM_MOVES):
        test_hash = Web3.soliditySha3(['uint256', 'bytes32'], [move, hex_salt]) #pylint: disable=E1120
        str_test_hash = hex_to_str(test_hash.hex())
        if str_test_hash == move_hash:
            return move

    reverse_hash_fail(hex_message)
    return -1

def _beat_move(_last_bot_move, _last_opponent_move, hex_message):
    return _incremental_move(_decode_move(hex_message))

def next_move(last_bot_move, last_opponent_move, addr, hex_message=None):
    bot_index = ADDRESSES.index(addr)
    if bot_index < 0:
        _raise_error()
    return STRATEGY[bot_index](last_bot_move, last_opponent_move, hex_message)

STRATEGY = [
    _pick_rock,
    _pick_increment,
    _pick_opponent_increment,
    _beat_move
]
