import random
import os
from bot.api.gpt import get_gpt_message

pretext_invalid_check = [
    "Boy ah, use the command like this:",
    "Say how many times already, use the command like this: ",
    "Wrong lah, like this:",
]


def create_invalid_check():
    if os.environ.get("USE_GPT_USING_SIWEI_MONEY", "False").lower() == "true":
        text = get_gpt_message(
            "The user has used an invalid command. Tell the user that they are wrong"
        )
    else:
        text = random.choice(pretext_invalid_check)
    return f"""
    {text}\r\n
/check <location1> to <location2>
"""
