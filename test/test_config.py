from bot.config import get_bot, K_NAME


def test_get_bot():
    bot2 = get_bot(index=0)
    assert bot2[K_NAME] == 'Young Bot'
