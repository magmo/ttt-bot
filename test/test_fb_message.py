import firebase_admin
import pytest

import bot.fb_message
from bot.config import ADDRESSES
from bot.util import str_to_hex


@pytest.mark.usefixtures("test_app")
def test_message_opponent_wallet(mocker):
    #pylint: disable=C0301
    message = '00000000000000000000000048BaCB9266a570d521063EF5dD96e61686DbE788000000000000000000000000000000000000000000000000000000000000000500000000000000000000000000000000000000000000000000000000000000020000000000000000000000001599c26e9DcAB9A8f2410481c4329E8502C548a60000000000000000000000002d7d467f6622f1f5a1cFf4C3787b615ACca191660000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004563918244f400000000000000000000000000000000000000000000000000004563918244f4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000de0b6b3a7640000'
    signature = '0xb0ef6e5f02c931e81c40d93375292edf36f2a661b02da606709c11778aecd6512c23c74ca448575297a9b14d93bd1ae81f7731c80b765859b5e77aa789a943711b'
    mocker.patch('firebase_admin.db.Reference.push')
    bot.fb_message.message_opponent(message, ADDRESSES[0])
    d_push = {'data': str_to_hex(
        message), 'signature': signature, 'queue': 'WALLET'}
    # pylint: disable=no-member
    firebase_admin.db.Reference.push.assert_called_once_with(
        d_push)


@pytest.mark.usefixtures("test_app")
def test_message_game_engine(mocker):
    #pylint: disable=C0301
    message = '000000000000000000000000c1912fee45d61c87cc5ea59dae31190fffff232d00000000000000000000000000000000000000000000000000000000000001c800000000000000000000000000000000000000000000000000000000000000020000000000000000000000005291fA3F70C8e3D21B58c831018E5a0D82Dc4ab90000000000000000000000009552ceb4e6fa8c356c1a76a8bc8b1efa7b9fb205000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000006a94d74f430000000000000000000000000000000000000000000000000000006a94d74f4300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002386f26fc10000'
    signature = '0x872695a7dd2591e95231bb91e7068baf927059e3d725cd8ddf547862498cbbff4703d2dca0878ceb3e86b06675b5c3f948ef83f4f0a9cd675c030fc36ea8f2861b'
    mocker.patch('firebase_admin.db.Reference.push')
    bot.fb_message.message_opponent(message, ADDRESSES[0])
    d_push = {'data': str_to_hex(
        message), 'signature': signature, 'queue': 'GAME_ENGINE'}
    # pylint: disable=no-member
    firebase_admin.db.Reference.push.assert_called_once_with(
        d_push)


@pytest.mark.usefixtures("test_app")
def test_message_consumed(mocker):
    # Need to get a valid key for an end to end test
    mocker.patch('firebase_admin.db.Reference.delete')
    bot.fb_message.message_consumed('-LNe4HoVe29ILP0kT177', ADDRESSES[0])
    firebase_admin.db.Reference.delete.assert_called_once()  # pylint: disable=no-member
