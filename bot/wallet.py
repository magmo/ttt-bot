from firebase_admin import db
from eth_account import Account
from eth_account.messages import defunct_hash_message
from web3 import Web3

from bot.config import get_bot
from bot.config import K_ADDRESS, K_PK, K_STAKE, K_WALLET_UID, STAKES_IN_FUNDING, TESTNET
from bot.util import hex_to_str, int_to_hex_str, str_to_hex, str_to_checksum_address
from bot.util import set_response_message

from bot import coder

K_WALLETS = 'wallets'
K_CHANNELS = 'channels'
K_RECEIVED = 'received'
K_SENT = 'sent'
K_UID = 'uid'
K_MESSAGE = 'message'
K_LAST_BOT_MOVE = 'last_bot_move'
K_LAST_OPPONENT_MOVE = 'last_opponent_move'
K_NONCE = 'nonce'

def _get_new_wallet(bot_addr):
    bot = get_bot(addr=bot_addr)
    return {
        'address': bot[K_ADDRESS],
        K_CHANNELS: None,
        'privateKey': bot[K_PK],
        K_UID: str_to_hex(bot[K_WALLET_UID]),
        K_NONCE: -1
    }

def _get_account(bot_addr):
    key = get_bot(addr=bot_addr)[K_PK]
    return Account.privateKeyToAccount(str_to_hex(key)) #pylint: disable=E1120

def get_wallets_ref():
    return db.reference().child(K_WALLETS)

def get_wallet_ref(wallet_key):
    return get_wallets_ref().child(wallet_key)

def get_wallet_channel_ref(bot_addr, hex_message):
    _wallet, wallet_key = get_wallet(bot_addr)
    channel_id = coder.get_channel_id(hex_message)

    return get_wallet_ref(wallet_key).child(K_CHANNELS).child(channel_id)

def create_wallet(bot_addr):
    get_wallets_ref().push(_get_new_wallet(bot_addr))

def get_wallet(bot_addr):
    uid = get_bot(addr=bot_addr)[K_WALLET_UID]
    hex_uid = str_to_hex(uid)
    wallets_ref = get_wallets_ref()
    bot_wallet_query = wallets_ref.order_by_child(K_UID).equal_to(hex_uid).limit_to_first(1)
    wrapped_wallet = bot_wallet_query.get()
    if not wrapped_wallet:
        create_wallet(bot_addr)
        wrapped_wallet = bot_wallet_query.get()

    return (list(wrapped_wallet.values())[0], list(wrapped_wallet.keys())[0])

def clear_wallet_channel(hex_message, bot_addr):
    get_wallet_channel_ref(bot_addr, hex_message).delete()

def clear_wallet_channels(bot_addr):
    _, wallet_key = get_wallet(bot_addr)
    get_wallet_ref(wallet_key).child(K_CHANNELS).delete()

def get_last_message_for_channel(hex_message, bot_addr):
    message_ref = get_wallet_channel_ref(bot_addr, hex_message).child(K_RECEIVED).child(K_MESSAGE)
    last_message = message_ref.get()
    return hex_to_str(last_message)

def set_last_message_for_channel(hex_message, bot_addr):
    message_ref = get_wallet_channel_ref(bot_addr, hex_message).child(K_RECEIVED).child(K_MESSAGE)
    message_ref.set(str_to_hex(hex_message))

def _get_last_move(hex_message, key, bot_addr):
    move_ref = get_wallet_channel_ref(bot_addr, hex_message).child(key)
    return move_ref.get()

def _set_last_move(hex_message, key, move, bot_addr):
    move_ref = get_wallet_channel_ref(bot_addr, hex_message).child(key)
    move_ref.set(move)

def get_last_opponent_move(hex_message, bot_addr):
    return _get_last_move(hex_message, K_LAST_OPPONENT_MOVE, bot_addr)

def set_last_opponent_move(hex_message, bot_addr):
    a_move = coder.get_game_aplay(hex_message)
    _set_last_move(hex_message, K_LAST_OPPONENT_MOVE, a_move, bot_addr)

def get_last_bot_move(hex_message, bot_addr):
    return _get_last_move(hex_message, K_LAST_BOT_MOVE, bot_addr)

def set_last_bot_move(hex_message, move, bot_addr):
    _set_last_move(hex_message, K_LAST_BOT_MOVE, move, bot_addr)

def sign_message(message, bot_addr):
    message_hash = Web3.sha3(hexstr=message)
    defunct_hash = defunct_hash_message(message_hash)
    acct = _get_account(bot_addr)
    signed_hash = acct.signHash(defunct_hash)
    return int_to_hex_str(signed_hash['r']) + int_to_hex_str(signed_hash['s']) \
        + int_to_hex_str(signed_hash['v'], 2)

def fund_adjudicator(contract_addr, bot_addr):
    infura_endpoint = f'https://{TESTNET}.infura.io/v3/2972b45cf9444a6d8f8695f6bdbc672f'
    from_addr = str_to_checksum_address(bot_addr)
    to_addr = str_to_checksum_address(contract_addr)

    provider = Web3.HTTPProvider(infura_endpoint)
    o_w3 = Web3(provider)
    eth_nonce = o_w3.eth.getTransactionCount(from_addr) #pylint: disable=E1101

    def increment_nonce(wallet_nonce):
        if wallet_nonce is None:
            return eth_nonce
        new_nonce = wallet_nonce + 1 if wallet_nonce >= eth_nonce else eth_nonce
        return new_nonce

    _, wallet_key = get_wallet(bot_addr)
    nonce = get_wallet_ref(wallet_key).child(K_NONCE).transaction(increment_nonce)

    stake = get_bot(addr=bot_addr)[K_STAKE]
    transaction = {
        'nonce': nonce,
        'from': from_addr,
        'to': to_addr,
        'value': stake * STAKES_IN_FUNDING,
        'gas': 100000,
        'gasPrice': o_w3.eth.gasPrice #pylint: disable=E1101
    }
    private_k = get_bot(addr=bot_addr)[K_PK]
    signed = o_w3.eth.account.signTransaction(transaction, private_k) #pylint: disable=E1101
    _sent_tx = o_w3.eth.sendRawTransaction(signed.rawTransaction) #pylint: disable=E1101
    return set_response_message('Funding success with transaction hash of ' + signed.hash.hex())
