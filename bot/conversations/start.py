import boto3
from bot.conversations.save import save
from telegram.ext import (
    ContextTypes,
    CallbackContext,
)
from telegram import Update
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
)
from bot.repository import (
    user as db_user,
    query as db_query,
    userTravelHistory as db_userTravelHistory,
    bookmark as db_bookmark,
)
import boto3
terms_and_conditions_text = "Hello, as we will be collecting data, please read and accept the <a href='https://www.privacypolicies.com/live/9cb11b76-45c7-41ad-8fd6-a69c4a57d864'>Privacy Terms and Conditions</a> before you use me."

START_ROUTES, SELECT_START_LOCATION, SELECT_END_LOCATION = range(3)
# # Callback data
ONE, TWO, THREE, FOUR = range(4)
ddb_resource = boto3.resource('dynamodb', endpoint_url='http://localhost:8000', 
                          region_name='us-west-2',
                          aws_access_key_id='fakekey',
                          aws_secret_access_key='fakeSecretKey')

user_table = ddb_resource.Table('User')
query_table = ddb_resource.Table('Query')
user_travel_history_table = ddb_resource.Table('UserTravelHistory')
bookmark_table = ddb_resource.Table('Bookmark')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user = update.message.from_user

    context.user_data["id"] = user.id
    context.user_data["first_name"] = user.first_name
    context.user_data["username"] = user.username

    if 'accepted_terms' not in user_data and not db_user.user_exists(user.id,user_table): #creates a boolean value
        user_data['accepted_terms'] = False
    # insert_interaction(user.id, 'start')

        Inlinekeyboard = [
            [
                InlineKeyboardButton(
                    text="Accept",
                    callback_data="accept"
                )
            ]
        ]

        # Send the message with the hyperlink
        await update.message.reply_html(
            terms_and_conditions_text,
            reply_markup=InlineKeyboardMarkup(Inlinekeyboard)
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=        """
Hello Ahboy or Ahgirl! I am your friendly neighbourhood auntie! Some call me Cheapo Auntie! 
I can help you find the cheapest transport options between two locations!

Here's what I can do:

1) /check location1 to location2 
Type it in the format above to check the prices

2) /add location1 to location2 
To add your specificied route to bookmarks

3) /list 
To list your bookmarked routes

4) /remove number
To remove the specified bookmark

5) /cancel 
To stop whatever you're currently doing

6) /help 
or troubleshooting
                                    """
        )
        return START_ROUTES

async def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    user_data = context.user_data

    if query.data == "accept":
        # Toggle the value of "terms_and_conditions" to True
        user_data['terms_and_conditions'] = True
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You have accepted the Privacy Terms and Conditions.")
        await query.message.edit_reply_markup(reply_markup=None)
        try:
            db_user.create_user({
                "user_id": user_data["id"],
                "first_name": user_data["first_name"],
                "username": user_data["username"],
            }, user_table)
        except Exception as e:
            print("Error creating user", e)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=        """
Hello Ahboy or Ahgirl! I am your friendly neighbourhood auntie! Some call me Cheapo Auntie! 
I can help you find the cheapest transport options between two locations!

Here's what I can do:
1) /check location1 to location2 - to check the prices
2) /add location1 to location2 - to add your specificied route to bookmarks
3) /list - to list your bookmarked routes
4) /remove number - to remove specified bookmark
5) /cancel - to stop whatever you're currently doing
6) /help - for troubleshooting
                                    """
        )
    else:
        await query.answer("Invalid button click.")

    return START_ROUTES
