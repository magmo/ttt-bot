import random
from bot.coder import get_game_noughts, get_game_crosses

VALID_MOVES = [
    1, 2, 4,
    8, 16, 32,
    64, 128, 256,
]


def next_move(hex_message):
    noughts = get_game_noughts(hex_message)
    crosses = get_game_crosses(hex_message)

    while True:
        move = VALID_MOVES[random.randint(0, 8)]
        if noughts | move != noughts and crosses | move != crosses:
            return move
