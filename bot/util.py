from web3 import Web3

HEX_PREFIX = '0x'

def hex_to_str(hex_str):
    if not hex_str or len(hex_str) < len(HEX_PREFIX):
        return hex_str
    return hex_str[len(HEX_PREFIX):]

def str_to_hex(string):
    return HEX_PREFIX + string

def int_to_field(num, min_length=64):
    h_num = format(num, 'x')
    format_str = '{:0>%d}' % min_length
    return format_str.format(h_num)

def int_to_hex_str(integer, min_length=64):
    return int_to_field(integer, min_length)


def str_to_checksum_address(string):
    w3_instance = Web3()
    hex_string = str_to_hex(string)
    return w3_instance.toChecksumAddress(hex_string)

def set_response_message(message='', response=None):
    if not response:
        response = dict()
    response['message'] = message
    return response
