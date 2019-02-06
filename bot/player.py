from flask import Blueprint, current_app, jsonify, request, g


from bot import challenge, coder, fb_message, strategy, wallet
from bot.util import hex_to_str, set_response_message, str_to_hex

BP = Blueprint('channel_message', __name__)

# Error definitions


class PlayerError(Exception):
    pass


class PlayerAError(PlayerError):
    def __str__(self):
        return 'The bot only plays as player B'


class PlayerGamePositionNotImplementedError(PlayerError):
    def __init__(self, game_position):
        super().__init__()
        self.game_position = game_position

    def __str__(self):
        return f'The {self.game_position} is not implemented'


class PlayerChannelStateNotImplementedError(PlayerError):
    def __init__(self, channel_state):
        super().__init__()
        self.channel_state = channel_state

    def __str__(self):
        return f'The {self.channel_state} is not implemented'


def undefined_game_position(game_position):
    raise PlayerGamePositionNotImplementedError(game_position)


# Game position transitions
def _transfer_stake(hex_message, multiplier=1):
    stake = coder.get_game_stake(hex_message)
    hex_message = coder.increment_state_balance(
        hex_message, 0, -1 * multiplier * stake)
    return coder.increment_state_balance(hex_message, 1, multiplier * stake)


def check_end_of_game(hex_message):
    if strategy.check_win(hex_message):
        hex_message = coder.update_game_position(hex_message, 2)
        return transfer_double_stake(hex_message)
    if strategy.check_draw(hex_message):
        hex_message = coder.update_game_position(hex_message, 3)
        return transfer_stake(hex_message)
    return transfer_double_stake(hex_message)


def transfer_double_stake(hex_message):
    return _transfer_stake(hex_message, 2)


def transfer_stake(hex_message):
    return _transfer_stake(hex_message)


def play_nought_move(hex_message):
    move = strategy.next_move(hex_message)
    noughts = coder.get_game_noughts(hex_message) + move
    return coder.update_noughts(hex_message, noughts)


def play_cross_move(hex_message):
    move = strategy.next_move(hex_message)
    crosses = coder.get_game_crosses(hex_message) + move
    return coder.update_crosses(hex_message, crosses)


def from_oplay(_hex_message):
    return [play_cross_move,
            lambda h_message: coder.change_game_position(h_message, -1), check_end_of_game]


def from_xplay(_hex_message):
    return [play_nought_move, coder.change_game_position, check_end_of_game]


def from_victory(hex_message):
    if not coder.get_state_balance(hex_message, 0) or not coder.get_state_balance(hex_message, 1):
        wallet.clear_wallet_channel(hex_message, g.bot_addr)
        return [coder.conclude]
    return [coder.play_again_me_first]


def from_draw(_hex_message):
    return [coder.play_again_me_first]


def from_play_again_me_first(_hex_message):
    return [coder.change_game_position]


def from_play_again_me_second(_hex_message):
    return [coder.update_noughts, transfer_stake, play_cross_move,
            lambda h_message: coder.update_game_position(h_message, 0)]


GAME_STATES = (
    from_xplay,
    from_oplay,
    from_victory,
    from_draw,
    from_play_again_me_first,
    from_play_again_me_second,
)


# Channel state transitions
def prefund_setup(hex_message):
    state_count = coder.get_state_count(hex_message)
    transformations = []
    if state_count:
        raise PlayerAError()
    else:
        transformations = [coder.increment_state_count]

    return transformations


def postfund_setup(hex_message):
    return prefund_setup(hex_message)


def game(hex_message):
    game_position = coder.get_game_position(hex_message)
    return GAME_STATES[game_position](hex_message)


def conclude(hex_message):
    wallet.clear_wallet_channel(hex_message, g.bot_addr)
    return []


CHANNEL_STATES = [
    prefund_setup,
    postfund_setup,
    game,
    conclude
]


# State machine
def transition_from_state(hex_message):
    channel_state = coder.get_channel_state(hex_message)
    message_transformations = CHANNEL_STATES[channel_state](hex_message)

    response_message = hex_message
    message_transformations += [coder.increment_state_turn_num]
    for transformation in message_transformations:
        response_message = transformation(response_message)

    return response_message


def game_engine_message(message, bot_addr):
    d_response = {}

    last_message = wallet.get_last_message_for_channel(message, bot_addr)
    if last_message == message:
        warning = f'Duplicate message received {last_message}'
        current_app.logger.warning(warning)
        # Turning off duplicate message safeguard for now
        # return set_response_message(warning, d_response)
    wallet.set_last_message_for_channel(message, bot_addr)

    coder.assert_channel_num_players(message)
    players = coder.get_channel_players(message)
    if bot_addr not in players:
        warning = 'The message players do not include a bot'
        current_app.logger.warning(warning)
        return set_response_message(warning, d_response)

    new_state = transition_from_state(message)

    current_app.logger.info(f'Sending opponent: {new_state}')
    fb_message.message_opponent(new_state, bot_addr)
    return set_response_message(str_to_hex(new_state), d_response)


@BP.route('/channel_message', methods=['POST'])
def channel_message():
    request_json = request.get_json()
    current_app.logger.info(f'Request_json: {request_json}')

    message = hex_to_str(request_json['data'])
    fb_message_key = request_json.get('message_key')
    fb_message.message_consumed(fb_message_key, g.bot_addr)

    d_response = set_response_message()

    if len(message) >= 64:
        d_response = game_engine_message(message, g.bot_addr)
    # A message of length 64 or shorter is an adjudicator address
    else:
        d_response = wallet.fund_adjudicator(message, g.bot_addr)
        current_app.logger.info(d_response.get('message'))

    return jsonify(d_response)


@BP.route('/clear_wallet_channels', methods=['POST'])
def clear_wallet():
    wallet.clear_wallet_channels(g.bot_addr)
    return jsonify({})


@BP.route('/create_challenge', methods=['POST'])
def create_challenge():
    challenge.create_new_challenge(g.bot_addr)
    return jsonify({})
