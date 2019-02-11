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


def minmax_strategy(hex_message, is_crosses):
    noughts = get_game_noughts(hex_message)
    crosses = get_game_crosses(hex_message)

    return _minmax(noughts, crosses, is_crosses, is_crosses, 0)[1]


def check_win(hex_message):
    noughts = get_game_noughts(hex_message)
    crosses = get_game_crosses(hex_message)
    if _check_position_win(noughts) or _check_position_win(crosses):
        return True
    return False


def check_draw(hex_message):
    noughts = get_game_noughts(hex_message)
    crosses = get_game_crosses(hex_message)
    return _check_draw(noughts, crosses)


def _check_position_win(position):
    for winning_position in WINNING_POSITIONS:
        if position & winning_position == winning_position:
            return True
    return False


def _check_draw(noughts, crosses):
    if noughts + crosses == DRAW:
        return True
    return False


def _check_minmax_win(noughts, crosses):
    if _check_position_win(noughts) or _check_position_win(crosses):
        return True
    return False


def _minmax(noughts, crosses, crosses_moves, is_crosses, depth):
    my_move = (crosses_moves and is_crosses) or (
        not crosses_moves and not is_crosses)
    my_best_move_value = -2
    opponent_best_move_value = 2
    best_move = None

    for move in VALID_MOVES:
        if noughts | move != noughts and crosses | move != crosses:
            noughts_after_move = noughts
            crosses_after_move = crosses
            if crosses_moves:
                crosses_after_move = crosses | move
            else:
                noughts_after_move = noughts | move

            if _check_minmax_win(noughts_after_move, crosses_after_move):
                if my_move:
                    return (1, move)
                else:
                    return (-1, move)

            if _check_draw(noughts_after_move, crosses_after_move):
                return (0, move)

            (move_val, _best_move) = _minmax(
                noughts_after_move, crosses_after_move, not crosses_moves, is_crosses, depth + 1)
            if my_move and move_val > my_best_move_value:
                my_best_move_value = move_val
                best_move = move
            elif not my_move and move_val < opponent_best_move_value:
                opponent_best_move_value = move_val
                best_move = move

    if my_move:
        if depth == 0 or depth == 1:
            print("My move " + str(noughts) + " " + str(crosses) + " " + str(best_move) +
                  " " + str(my_best_move_value) + " " + str(depth))
        return (my_best_move_value, best_move)

    if depth == 0 or depth == 1:
        print("Opponent move " + str(noughts) + " " + str(crosses) + " " + str(best_move) +
              " " + str(opponent_best_move_value) + " " + str(depth))
    return (opponent_best_move_value, best_move)
