import random
import os
from dotenv import load_dotenv

from bot.api.gpt import get_gpt_message

load_dotenv()

pretext_price_query = [
    "Knn, here's your prices",
    "Eh, here's prices la boy",
    "Auntie very tired liao, happy already?",
    "Walao, so many to compare, but ok lah, got your prices here."
    "Oi, see liao bo? I find all the prices for you already, faster check."
    "Steady lah, all the best prices compiled for you. Satisfied not?"
    "Don't say bojio, I give you all the good deals already, hor."
    "Aiyah, so mafan but for you, I do. Check the prices out."
    "Hoseh liao, all the prices you need, right here. Happy or not?"
    "Lai, I show you all the cheap and good ones. You thank auntie, ok?"
    "Wah, you really make me work, but ok lah, got your prices."
    "Si bei sian to find all these, but for you, I got it sorted liao."
    "Paiseh ah, took a bit long. But got all your price comparisons here.",
    "Alamak, you ask so much! But don't worry lah, got all your prices here. Shiok or not?"
    "Eh, macha, see already ah? I find all for you, lepak corner and check."
    "Auntie really penat, lah. But look, all your prices got already. Jom check!"
    "Wah, you make me kelam kabut, but ok lah, all the good deals are here. Can?"
    "Oi, dei, all your price comparisons here already. Full power, satisfied?"
    "Steady pom pi pi! Got all the prices for you. Now your pocket happy?"
    "Walao eh, so demanding. But because it's you, I kasi you all the best deals."
    "See lah, bro, all the cheapest ones I find for you already. Don't play play, check it out."
    "Eh, you think very senang is it? But ok lah, for you, I do already. Ini macam ok?"
]

pretext_loading = [
    "Wait ah, auntie finding",
    "Mafan leh you boy",
    "Very fast one, you count to 10 first",
    "Hold up, lah. Doing fast-fast."
    "Aiyo, why so kan cheong? Give me sec lah."
    "Relax lah brother, I speed up for you."
    "Eh, give chance lah. I'm on it already."
    "Simi sai also want fast? Coming, coming."
    "Don't pray pray, I make it quick one."
    "Aiyah, wait lah. Not so jialat one."
    "Haiyah, you rush like siao. Ok, ok, doing already."
    "Walao, you think what? Rocket ah? Ok wait ah."
    "Steady lah, I make magic happen now.",
    "Chill lah, I jalan fast-fast."
    "Oei, no hurry lah. Good things must wait one."
    "Kiasi ah you? Trust auntie, I settle soon."
    "Paiseh hor, making you wait. Almost done lah."
    "Eh, not so fast can or not? Working on it lah."
    "Bojio! You think so easy ah? Okok, I try speed up."
    "Wait long long also can. I faster than MRT lah!"
    "Aiya, tap tap tap, see? Doing already lah."
    "Eh hello, patience is a virtue hor. Coming already."
    "Slowly lah, good stuff no need to rush one."
    "Kampong spirit mah, help you sure can. Wait ah."
    "Alamak, so demanding. Ok ok, I faster work."
    "Got so urgent meh? Ok lah, for you I fast hand fast leg."
    "Sabar sabar, my friend. Good things coming your way."
    "Eh, your horse run so fast, wait I catch up can?"
    "Aiyo, relax lah. I make it chop chop for you."
    "Siao liao, so much to do. Ok, you first lah."
    "Wah lau eh, no panic. Auntie is on it already."
    "Can wait not? I make sure worth the wait one."
]

pretext_choose_start = [
    "Auntie give you one list, you just choose from here"
]

pretext_choose_end = [
    "Ok, now you choose where you want go for me, cepat lah"
]


def create_loading_message():
    if os.environ.get("USE_GPT_USING_SIWEI_MONEY", "False").lower() == "true":
        return get_gpt_message(
            "Formulate a message that tells the user to wait, and that it should take a few seconds. Here are some references that you MUST change and modify from:" + '\n'.join(pretext_loading)
        )
    else:
        return random.choice(pretext_loading)


def create_price_query_message(gojek_price: float, tada_price: float, zig_price: float):
    if os.environ.get("USE_GPT_USING_SIWEI_MONEY", "False").lower() == "true":
        text = get_gpt_message(
            "The bot has found prices for the user. You don't have to give the prices, you just have to provide the message for it in Singlish. Tell the user the following are the prices. Keep your responses down to two sentences. Here are some references that you MUST change and modify from:" + '\n'.join(pretext_loading), 100
        )
    else:
        text = random.choice(pretext_price_query)
    message = f"""
{text}\r\n
Gojek - ${gojek_price}
Tada - ${tada_price}
Zig - ${zig_price}
         """
    return message

def create_choose_start():
    return random.choice(pretext_choose_start)

def create_choose_end():
    return random.choice(pretext_choose_end)

