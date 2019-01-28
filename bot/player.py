from flask import Blueprint, current_app, jsonify, request, g


from bot import challenge, coder, fb_message, strategy, wallet
from bot.tracking import track_ge_event, track_wallet_event
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
def playera_pays_playerb(hex_message):
    stake = coder.get_game_stake(hex_message)
    hex_message = coder.increment_state_balance(hex_message, 0, -1 * stake)
    return coder.increment_state_balance(hex_message, 1, stake)

def play_move(hex_message):
    bot_addr = g.bot_addr
    last_opponent_move = wallet.get_last_opponent_move(hex_message, bot_addr)
    last_bot_move = wallet.get_last_bot_move(hex_message, bot_addr)
    move = strategy.next_move(last_bot_move, last_opponent_move, bot_addr, hex_message=hex_message)
    wallet.set_last_bot_move(hex_message, move, bot_addr)
    return coder.update_move(hex_message, move)

def from_game_propose(_hex_message):
    track_ge_event(g.bot_addr, "from_game_propose")
    return [playera_pays_playerb, play_move, coder.increment_game_position]

def from_game_reveal(hex_message):
    track_ge_event(g.bot_addr, "from_game_reveal")
    wallet.set_last_opponent_move(hex_message, g.bot_addr)
    if not coder.get_state_balance(hex_message, 0) or not coder.get_state_balance(hex_message, 1):
        wallet.clear_wallet_channel(hex_message, g.bot_addr)
        return [coder.conclude]
    return [coder.new_game]

GAME_STATES = (
    lambda x: undefined_game_position('FromGameResting'),
    from_game_propose,
    lambda x: undefined_game_position('FromGameAccept'),
    from_game_reveal
)


# Channel state transitions
def prefund_setup(hex_message):
    track_ge_event(g.bot_addr, "prefund")
    state_count = coder.get_state_count(hex_message)
    transformations = []
    if state_count:
        raise PlayerAError()
    else:
        transformations = [coder.increment_state_count]

    return transformations

def postfund_setup(hex_message):
    track_ge_event(g.bot_addr, "postfund")
    return prefund_setup(hex_message)

def game(hex_message):
    game_position = coder.get_game_position(hex_message)
    return GAME_STATES[game_position](hex_message)

def conclude(hex_message):
    track_ge_event(g.bot_addr, "conclude")
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
        track_wallet_event(g.bot_addr, "from_game_propose")
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
