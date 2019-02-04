#pylint: disable=C0301
import firebase_admin
import bot.player
from bot.challenge import _get_new_challenge
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
        state = '000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c800000000000000000000000000000000000000000000000000000000000000020000000000000000000000005291fA3F70C8e3D21B58c831018E5a0D82Dc4ab900000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006a94d74f430000000000000000000000000000000000000000000000000000006a94d74f4300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc10000'
        new_state = '000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c800000000000000000000000000000000000000000000000000000000000000020000000000000000000000005291fA3F70C8e3D21B58c831018E5a0D82Dc4ab900000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000006a94d74f430000000000000000000000000000000000000000000000000000006a94d74f4300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc10000'
        state_machine_transition(state, new_state)


def test_black_box_postfund(test_app):
    with test_app.test_request_context('channel_message'):
        state = '000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c800000000000000000000000000000000000000000000000000000000000000020000000000000000000000005291fA3F70C8e3D21B58c831018E5a0D82Dc4ab900000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006a94d74f430000000000000000000000000000000000000000000000000000006a94d74f4300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc10000'
        new_state = '000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c800000000000000000000000000000000000000000000000000000000000000020000000000000000000000005291fA3F70C8e3D21B58c831018E5a0D82Dc4ab900000000000000000000000055de2e479F3D0183D95f5A969bEEB3a147F60049000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000006a94d74f430000000000000000000000000000000000000000000000000000006a94d74f4300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc10000'
        state_machine_transition(state, new_state)


def test_black_box_from_x_move(test_app, mocker):
    with test_app.test_request_context('channel_message'):
        mocker.patch('random.randint', lambda _x, _y: 0)
        state = '00000000000000000000000007f96aa816c1f244cbc6ef114bb2b023ba54a2eb000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000020000000000000000000000001251659F5A4897bBebeB949E6Df22697d43C42dC000000000000000000000000A317E78f9F62Bc4959D0682F30043B9C0797C74F00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044364c5bb00000000000000000000000000000000000000000000000000000002d79883d2000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000b5e620f4800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020'
        new_state = '00000000000000000000000007f96aa816c1f244cbc6ef114bb2b023ba54a2eb000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000020000000000000000000000001251659F5A4897bBebeB949E6Df22697d43C42dC000000000000000000000000A317E78f9F62Bc4959D0682F30043B9C0797C74F0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002d79883d2000000000000000000000000000000000000000000000000000000044364c5bb000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000b5e620f4800000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000020'
        state_machine_transition(state, new_state)


def test_black_box_from_o_move(test_app, mocker):
    with test_app.test_request_context('channel_message'):
        mocker.patch('random.randint', lambda _x, _y: 0)
        state = '0000000000000000000000008d61158a366019ac78db4149d75fff9dda51160d000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000020000000000000000000000001251659F5A4897bBebeB949E6Df22697d43C42dC000000000000000000000000A317E78f9F62Bc4959D0682F30043B9C0797C74F0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004f94ae6af8000000000000000000000000000000000000000000000000000000221b262dd800000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000b5e620f4800000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000020'
        new_state = '0000000000000000000000008d61158a366019ac78db4149d75fff9dda51160d000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000020000000000000000000000001251659F5A4897bBebeB949E6Df22697d43C42dC000000000000000000000000A317E78f9F62Bc4959D0682F30043B9C0797C74F0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000d000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000038d7ea4c6800000000000000000000000000000000000000000000000000000038d7ea4c6800000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000b5e620f4800000000000000000000000000000000000000000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000021'
        state_machine_transition(state, new_state)


def test_black_box_from_victory(test_app):
    with test_app.test_request_context('channel_message'):
        state = '00000000000000000000000007f96aa816c1f244cbc6ef114bb2b023ba54a2eb000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000020000000000000000000000001251659F5A4897bBebeB949E6Df22697d43C42dC000000000000000000000000A317E78f9F62Bc4959D0682F30043B9C0797C74F00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000008000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044364c5bb00000000000000000000000000000000000000000000000000000002d79883d2000000000000000000000000000000000000000000000000000000000000000000030000000000000000000000000000000000000000000000000000b5e620f4800000000000000000000000000000000000000000000000000000000000000000180000000000000000000000000000000000000000000000000000000000000124'
        new_state = '00000000000000000000000007f96aa816c1f244cbc6ef114bb2b023ba54a2eb000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000020000000000000000000000001251659F5A4897bBebeB949E6Df22697d43C42dC000000000000000000000000A317E78f9F62Bc4959D0682F30043B9C0797C74F00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000009000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044364c5bb00000000000000000000000000000000000000000000000000000002d79883d2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000b5e620f48000'
        state_machine_transition(state, new_state)


def test_black_box_from_resting(test_app, mocker):
    with test_app.test_request_context('channel_message'):
        mocker.patch('random.randint', lambda _x, _y: 0)
        state = '00000000000000000000000007f96aa816c1f244cbc6ef114bb2b023ba54a2eb000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000020000000000000000000000001251659F5A4897bBebeB949E6Df22697d43C42dC000000000000000000000000A317E78f9F62Bc4959D0682F30043B9C0797C74F0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000044364c5bb00000000000000000000000000000000000000000000000000000002d79883d2000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000b5e620f48000'
        new_state = '00000000000000000000000007f96aa816c1f244cbc6ef114bb2b023ba54a2eb000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000020000000000000000000000001251659F5A4897bBebeB949E6Df22697d43C42dC000000000000000000000000A317E78f9F62Bc4959D0682F30043B9C0797C74F0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000b000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000038d7ea4c6800000000000000000000000000000000000000000000000000000038d7ea4c6800000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000b5e620f4800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001'
        state_machine_transition(state, new_state)
