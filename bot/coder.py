from web3 import Web3
from bot.util import int_to_field, str_to_checksum_address

CHARS_PER_BYTE = 2
N_PLAYERS = 2
F_WIDTH = 32
ADDRESS_WIDTH = 20

#               type,     nonce,    nPlayers, [players]
CHANNEL_BYTES = F_WIDTH + F_WIDTH + F_WIDTH + F_WIDTH * N_PLAYERS
STATE_OFFSET = CHANNEL_BYTES

#             stateType, turnNum, stateCount, [balances]
STATE_BYTES = F_WIDTH + F_WIDTH + F_WIDTH + F_WIDTH * N_PLAYERS

''' RockPaperScissors Game Fields
    (relative to game offset)
    ==============================
    [  0 -  31] enum positionType
    [ 32 -  63] uint256 stake
    [ 64 -  95] bytes32 preCommit
    [ 96 - 127] enum bPlay
    [128 - 159] enum aPlay
    [160 - 191] bytes32 salt
    [192 - 223] uint256 roundNum
'''
GAME_OFFSET = STATE_OFFSET + STATE_BYTES


class CoderError(Exception):
    pass


class NumPlayersError(CoderError):
    def __init__(self, num_players):
        super().__init__()
        self.num_players = num_players

    def __str__(self):
        return f'Rock-paper-scissors requires exactly ' + \
            '{N_PLAYERS} players. {self.num_players} provided.'


def _extract_bytes(h_string, byte_offset=0, num_bytes=F_WIDTH):
    char_offset = byte_offset * CHARS_PER_BYTE
    return h_string[char_offset:char_offset + num_bytes * CHARS_PER_BYTE]


def _extract_int(h_string, byte_offset=0, num_bytes=32):
    return int(_extract_bytes(h_string, byte_offset, num_bytes), 16)


def _get_address_from_field(field):
    address = field[CHARS_PER_BYTE * (F_WIDTH - ADDRESS_WIDTH):]
    return address.lower()


def _get_byte_attribute_at_offset(h_message, offset, attr_index):
    return _extract_bytes(h_message, offset + F_WIDTH * attr_index)


def _get_int_attribute_at_offset(h_message, offset, attr_index):
    return _extract_int(h_message, offset + F_WIDTH * attr_index)


def _update_field(h_message, offset, attr_index, new_field):
    field_offset = (offset + F_WIDTH * attr_index) * CHARS_PER_BYTE
    prefix = h_message[:field_offset]
    suffix = h_message[field_offset + F_WIDTH * CHARS_PER_BYTE:]
    return prefix + new_field + suffix

# Channel attribute getters


def _get_channel_byte_attribute(h_message, attr_index):
    return _get_byte_attribute_at_offset(h_message, 0, attr_index)


def _get_channel_int_attribute(h_message, attr_index):
    return _get_int_attribute_at_offset(h_message, 0, attr_index)


def get_channel_type(h_message):
    channel_type = _get_channel_byte_attribute(h_message, 0)
    return _get_address_from_field(channel_type)


def get_channel_nonce(h_message):
    return _get_channel_int_attribute(h_message, 1)


def get_channel_num_players(h_message):
    num_players = _get_channel_int_attribute(h_message, 2)
    if num_players != N_PLAYERS:
        raise NumPlayersError(num_players)
    return num_players


def assert_channel_num_players(h_message):
    get_channel_num_players(h_message)


def get_channel_players(h_message):
    player_a = _get_channel_byte_attribute(h_message, 3)
    player_b = _get_channel_byte_attribute(h_message, 4)
    return [_get_address_from_field(player_a), _get_address_from_field(player_b)]


def get_channel_id(h_message):
    w3_instance = Web3()
    channel_type = get_channel_type(h_message)
    channel_nonce = get_channel_nonce(h_message)
    channel_players = get_channel_players(h_message)

    channel_type = str_to_checksum_address(channel_type)
    channel_type = w3_instance.toChecksumAddress(channel_type)
    channel_players = list(map(str_to_checksum_address, channel_players))

    return Web3().soliditySha3(
        ['address', 'uint256', 'address[]'],
        [channel_type, channel_nonce, channel_players]).hex()

# State attribute getters


def _get_state_int_attribute(h_message, attr_index):
    return _get_int_attribute_at_offset(h_message, STATE_OFFSET, attr_index)


def get_channel_state(h_message):
    return _get_state_int_attribute(h_message, 0)


def get_state_turn_num(h_message):
    return _get_state_int_attribute(h_message, 1)


def get_state_count(h_message):
    return _get_state_int_attribute(h_message, 2)


def get_state_balance(h_message, player_index):
    return _get_state_int_attribute(h_message, 3 + player_index)


def set_state_count(h_message, state_count):
    return _update_field(h_message, STATE_OFFSET, 2, int_to_field(state_count))


def increment_state_turn_num(h_message):
    turn_num = get_state_turn_num(h_message)
    turn_num += 1
    return _update_field(h_message, STATE_OFFSET, 1, int_to_field(turn_num))


def incerement_channel_state(h_message):
    channel_state = get_channel_state(h_message) + 1
    return _update_field(h_message, STATE_OFFSET, 0, int_to_field(channel_state))


def increment_state_count(h_message):
    state = get_state_count(h_message)
    state += 1
    return set_state_count(h_message, state)


def increment_state_balance(h_message, player_index, delta):
    balance = get_state_balance(h_message, player_index)
    balance += delta
    return _update_field(h_message, STATE_OFFSET, 3 + player_index, int_to_field(balance))

# Game attribute getters


def _get_game_byte_attribute(h_message, attr_index):
    return _get_byte_attribute_at_offset(h_message, GAME_OFFSET, attr_index)


def _get_game_int_attribute(h_message, attr_index):
    return _get_int_attribute_at_offset(h_message, GAME_OFFSET, attr_index)


def get_game_position(h_message):
    return _get_game_int_attribute(h_message, 0)


def get_game_stake(h_message):
    return _get_game_int_attribute(h_message, 1)


def get_game_precommit(h_message):
    return _get_game_byte_attribute(h_message, 2)


def get_game_bplay(h_message):
    return _get_game_int_attribute(h_message, 3)


def get_game_aplay(h_message):
    return _get_game_int_attribute(h_message, 4)


def get_game_salt(h_message):
    return _get_game_byte_attribute(h_message, 5)


def update_game_position(h_message, game_position):
    return _update_field(h_message, GAME_OFFSET, 0, int_to_field(game_position))


def increment_game_position(h_message):
    game_position = get_game_position(h_message)
    game_position += 1
    return update_game_position(h_message, game_position)


def new_game(h_message):
    h_message = update_game_position(h_message, 0)
    return h_message[: CHARS_PER_BYTE * (GAME_OFFSET + F_WIDTH * 2)]


def conclude(h_message):
    h_message = incerement_channel_state(h_message)
    h_message = set_state_count(h_message, 0)
    return h_message[: CHARS_PER_BYTE * (GAME_OFFSET)]


def update_move(h_message, move):
    return _update_field(h_message, GAME_OFFSET, 3, int_to_field(move))
