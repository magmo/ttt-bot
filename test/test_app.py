#pylint: disable=C0301
import firebase_admin
import flask
import bot.player
from bot.challenge import _get_new_challenge
from bot.config import ADDRESSES
from bot.util import str_to_hex
from util import get_bot0_addr, get_wallets_fn

SAMPLE_MESSAGE = '0x000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c8000000000000000000000000000000000000000000000000000000000000000200000000000000000000000063422d2F15a64F965B11B26AF46aDFba5324295e00000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005a000000000000000000000000000000000000000000000000000000000000005a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001e'
SAMPLE_RESPONSE = '0x000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c8000000000000000000000000000000000000000000000000000000000000000200000000000000000000000063422d2F15a64F965B11B26AF46aDFba5324295e00000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000005a000000000000000000000000000000000000000000000000000000000000005a0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001e'

### HELPERS ###


def mock_fb(mocker, wallet_json='wallets'):
    mocker.patch('firebase_admin.db.Query.get',
                 new=get_wallets_fn(wallet_json))
    mocker.patch('firebase_admin.db.Reference.delete', autospec=True)
    mocker.patch('firebase_admin.db.Reference.get', autospec=True)
    mocker.patch('firebase_admin.db.Reference.push', autospec=True)
    mocker.patch('firebase_admin.db.Reference.set', autospec=True)
    mocker.patch('firebase_admin.db.Reference.update', autospec=True)
    mocker.patch('firebase_admin.db.Reference.transaction', lambda _1, _2: 10)

### TESTS ###


def test_channel_message_clean_wallet(client, mocker):
    mock_fb(mocker)

    response = client.post('/channel_message', json={
        'data': SAMPLE_MESSAGE,
        'queue': 'GAME_ENGINE',
        'message_key': 'key123',
        'address_key': get_bot0_addr()
    })

    assert response.status_code == 200
    assert response.json['message'] == SAMPLE_RESPONSE


# Duplicate safeguard is off for now
"""def test_channel_message_duplicate_message(client, mocker):
    mock_fb(mocker, 'wallets_duplicate_message')
    mocker.patch('firebase_admin.db.Reference.get', lambda _1: SAMPLE_MESSAGE)

    response = client.post('/channel_message', json={
        'data': SAMPLE_MESSAGE,
        'queue': 'GAME_ENGINE',
        'message_key': 'key123',
        'address_key': get_bot0_addr()
    })

    assert response.status_code == 200
    assert response.json['message'] == f'Duplicate message received {hex_to_str(SAMPLE_MESSAGE)}'
"""  # pylint: disable=W0105


def test_channel_wallet_message(client, mocker):
    mock_fb(mocker)
    mocker.patch('web3.eth.Eth.sendRawTransaction', autospec=True)

    response = client.post('/channel_message', json={
        'data': '0xcdb594a32b1cc3479d8746279712c39d18a07fc0',
        'queue': 'WALLET',
        'message_key': 'key123',
        'address_key': get_bot0_addr()
    })

    assert response.status_code == 200


def test_create_challenge(client, mocker):
    mocker.patch('firebase_admin.db.Reference', autospec=True)

    response = client.post('/create_challenge', json={
        'address_key': get_bot0_addr()
    })
    assert response.status_code == 200
    firebase_admin.db.Reference().child('challenges').child(
        str_to_hex(get_bot0_addr())).set.assert_called_once_with(_get_new_challenge(0))

# Black-box testing


def state_machine_transition(state, new_state):
    assert bot.player.transition_from_state(state) == new_state


def test_black_box_prefund(test_app):
    with test_app.test_request_context('channel_message'):
        flask.g.bot_addr = ADDRESSES[0]
        state = '000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c800000000000000000000000000000000000000000000000000000000000000020000000000000000000000005291fA3F70C8e3D21B58c831018E5a0D82Dc4ab900000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006a94d74f430000000000000000000000000000000000000000000000000000006a94d74f4300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc10000'
        new_state = '000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c800000000000000000000000000000000000000000000000000000000000000020000000000000000000000005291fA3F70C8e3D21B58c831018E5a0D82Dc4ab900000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000006a94d74f430000000000000000000000000000000000000000000000000000006a94d74f4300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc10000'
        state_machine_transition(state, new_state)


def test_black_box_postfund(test_app):
    with test_app.test_request_context('channel_message'):
        flask.g.bot_addr = ADDRESSES[0]
        state = '000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c800000000000000000000000000000000000000000000000000000000000000020000000000000000000000005291fA3F70C8e3D21B58c831018E5a0D82Dc4ab900000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006a94d74f430000000000000000000000000000000000000000000000000000006a94d74f4300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc10000'
        new_state = '000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c800000000000000000000000000000000000000000000000000000000000000020000000000000000000000005291fA3F70C8e3D21B58c831018E5a0D82Dc4ab900000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000006a94d74f430000000000000000000000000000000000000000000000000000006a94d74f4300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc10000'
        state_machine_transition(state, new_state)
