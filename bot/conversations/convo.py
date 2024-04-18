from bot.api.gpt import call_gpt, get_gpt_message
from telegram.ext import (
    ContextTypes,
)
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
)
import tiktoken
START_ROUTES, SELECT_START_LOCATION, SELECT_END_LOCATION = range(3)

def summarize(summary: str, conversation: str) -> str:
    prompt = f'Summarize the conversation for me. Past summary:\n {summary}\n Conversation:\n {conversation}\n'
    new_summary = call_gpt(prompt, 3800)
    
    return new_summary


def generate_prompt(summary: str, conversation: str, input: str):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    current_prompt = f'Conversation Summary:\n {summary}\n Past Conversation:\n {conversation}\n Current user message: {input}\n Generate a reply, do not prefix yourself as the third-person. Just give the reply that can be read off normally.'
    num_tokens = len(enc.encode(current_prompt))
    print(f'Num tokens: {num_tokens}')
    print(f"Current Prompt: {current_prompt}")
    new_summary = None
    if num_tokens >= 4000:
        new_summary = summarize(summary, conversation)
        current_prompt = f'Conversation Summary:\n {new_summary}\n Current user message: {input}\n Generate a reply, do not prefix yourself as the third-person. Just give the reply that can be read off normally.'
    
    reply = get_gpt_message(current_prompt, 100)
    
    return (reply, new_summary)

def generate_ad_prompt(conversation: str, input: str):
    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
    summary = "The user is waiting for CheapoAuntie to tell him/her about the advertising material"
    current_prompt = f'Conversation Summary:\n{summary}\n Past Conversation:\n {conversation}\n Current Advertising content: {input}\n Generate a promotional message, do not prefix yourself as the third-person. Just give the reply that can be read off normally.'
    num_tokens = len(enc.encode(current_prompt))
    print(f'Num tokens: {num_tokens}')
    print(f"Current Prompt: {current_prompt}")
    new_summary = None
    if num_tokens >= 4000:
        new_summary = summarize(summary, conversation)
        current_prompt = f'Conversation Summary:\n {new_summary}\n Current Advertising: {input}\n Generate a promotional message, do not prefix yourself as the third-person. Just give the reply that can be read off normally.'
    
    reply = get_gpt_message(current_prompt, 100)
    
    return (reply, new_summary)

async def handle_ad_convo(update: Update, context: ContextTypes.DEFAULT_TYPE, input: str) -> int:
    summary = context.user_data.get("summary", "")
    conversation = context.user_data.get("conversation", "")
    

    print(f'Summary: {summary}')
    print(f'Conversation: {conversation}')
    
    reply, new_summary = generate_ad_prompt(conversation, input)

    context.user_data["summary"] = summary if new_summary is None else new_summary
    context.user_data["conversation"] = conversation + f"\n{input}" + f"\nCheapoAuntie: {reply}"
    print(f"Reply: {reply}")

    return reply

async def handle_convo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    summary = context.user_data.get("summary", "")
    conversation = context.user_data.get("conversation", "")
    user_input = f'User: {update.message.text}'

    print(f'Summary: {summary}')
    print(f'Conversation: {conversation}')
    
    reply, new_summary = generate_prompt("The user told CheapoAuntie about how he is struggling with finances", conversation, user_input)

    context.user_data["summary"] = summary if new_summary is None else new_summary
    context.user_data["conversation"] = conversation + f"\n{user_input}" + f"\nCheapoAuntie: {reply}"
    print(f"Reply: {reply}")


    await update.message.reply_text(reply)

    return START_ROUTES