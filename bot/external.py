import requests

from bot.coder import get_channel_players, get_game_precommit

SLACK_HOOK = 'https://hooks.slack.com/services/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'

def reverse_hash_fail(hex_message):
    players = get_channel_players(hex_message)
    move_hash = get_game_precommit(hex_message)
    message = f'Stumped by player {players[0]}. Cannot decrypt move hash {move_hash}'
    requests.post(SLACK_HOOK, json={'text': message})
