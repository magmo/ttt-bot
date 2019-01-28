import argparse

FIELDS = [
    'type',
    'nonce',
    'nPlayers',
    'address a',
    'address b',
    'state type',
    'turn num',
    'state count',
    'balance a',
    'balance b',
    'game position',
    'stake',
    'game precommit',
    'bPlay',
    'aPlay',
    'salt'
]
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("message")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    # Remove '0x'
    message = args.message
    if message[:2] == '0x':
        message = args.message[2:]
    counter = 0

    print()
    print()

    for i in range(0, len(message), 64):
        out = message[i:i+64]
        if args.verbose:
            out += ' -- ' + FIELDS[counter]
        print(out)
        counter += 1

if __name__ == '__main__':
    main()
