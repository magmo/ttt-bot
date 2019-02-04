import random
from bot.coder import get_game_noughts, get_game_crosses

VALID_MOVES = [
    1, 2, 4,
    8, 16, 32,
    64, 128, 256,
]

WINNING_POSITIONS = [448, 56, 7, 292, 146, 73, 273, 84]
DRAW = 511


def next_move(hex_message):
    noughts = get_game_noughts(hex_message)
    crosses = get_game_crosses(hex_message)

    while True:
        move = VALID_MOVES[random.randint(0, 8)]
        if noughts | move != noughts and crosses | move != crosses:
            return move


def check_win(hex_message):
    noughts = get_game_noughts(hex_message)
    crosses = get_game_crosses(hex_message)
    if noughts in WINNING_POSITIONS or crosses in WINNING_POSITIONS:
        return True
    return False


def check_draw(hex_message):
    noughts = get_game_noughts(hex_message)
    crosses = get_game_crosses(hex_message)
    if noughts + crosses == DRAW:
        return True
    return False
