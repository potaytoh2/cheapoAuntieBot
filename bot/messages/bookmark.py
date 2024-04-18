import random
import os
from bot.api.gpt import get_gpt_message

pretext_list_bookmark = [
    "Auntie remember for you already: ",
    "Auntie memory very good one: ",
    "Auntie got you covered already, no worry lah: "
    "Auntie's brain like computer, remember all: "
    "Eh, you think Auntie forget is it? Check this out lah: "
    "Auntie always keep in mind one, see here: "
    "Confirm plus chop, Auntie list down for you already: "
]

pretext_saved_bookmark = [
    "Auntie remember for you liao, won't forget one",
    "Small thing also want me to help you ah, youngsters nowadays ah",
    "Auntie jot down liao, sure won't miss out one",
    "Aiyah, so easy also need Auntie, but okay lah, done already",
    "Lai, Auntie do for you already, happy now?",
    "Eh, no need to worry, Auntie save for you like treasure",
    "Confirm Auntie remember, like how I remember to eat rice",
]

def create_list_bookmark_message():
    if os.environ.get("USE_GPT_USING_SIWEI_MONEY", "False").lower() == "true":
        text = get_gpt_message(
            "The bot will return a list of bookmark of paths. You don't have to provide the bookmark data. Tell the user that here are the list of bookmarks. Here are some references that you MUST change and modify from:" + '\n'.join(pretext_list_bookmark)
        )
    else:
        text = random.choice(pretext_list_bookmark)

    return f"{text}\r\n\r\n"


def create_saved_bookmark_message():
    if os.environ.get("USE_GPT_USING_SIWEI_MONEY", "False").lower() == "true":
        text = get_gpt_message(
            "The bot will successfully saved a path. Tell the user that it was a success. Here are some references that you MUST change and modify from:" + '\n'.join(pretext_saved_bookmark)
        )
    else:
        text = random.choice(pretext_saved_bookmark)

    return f"{text}\r\n\r\nUse /list to see all your bookmarks"
