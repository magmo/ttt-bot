import requests

JSON1 = {
    'data': '0x2313BbAEcca3fC7f9650eDD62Bc21A7C835f8bc8',
    'queue': 'WALLET',
    'message_key': '-LPoGMyaqrbGs8F8euzm',
    'address_key': '0x55de2e479f3d0183d95f5a969beeb3a147f60049'
}

JSON2 = {
    'data': '0xC74e5956Cf0943d8329dEd9163Ce52c79598606d',
    'queue': 'WALLET',
    'message_key': '-LPnw2V_xMni5hRjlWk-',
    'address_key': '0x55de2e479f3d0183d95f5a969beeb3a147f60049'
}

JSON3 = {
    'data': '0x39236C83119aC32146a6141927Bf169FAb268E2A',
    'queue': 'WALLET',
    'message_key': '-LPgKpC_VXgE0OtlibuY',
    'address_key': '0x55de2e479f3d0183d95f5a969beeb3a147f60049'
}

JSON4 = {
    'data': '0x55DCca276CfC34C4d7d9f1FA7c6E54A59D58274f',
    'queue': 'WALLET',
    'message_key': '-LPTN8xEYAK2jPoFyYt7',
    'address_key': '0x55de2e479f3d0183d95f5a969beeb3a147f60049'
}

def make_request(json):
    return requests.post('http://127.0.0.1:4000/channel_message', json=json)

if __name__ == '__main__':
    PAYLOADS = [JSON1, JSON2, JSON3, JSON4]
    for payload in PAYLOADS:
        r = make_request(payload)
        addr = r.json()['message'][40:]
        print("https://ropsten.etherscan.io/tx/" + addr)
