from bot.conversations.save import save
from telegram.ext import (
    ContextTypes,
    CallbackContext,
)
from telegram import Update

START_ROUTES, SELECT_START_LOCATION, SELECT_END_LOCATION = range(3)
# # Callback data
ONE, TWO, THREE, FOUR = range(4)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_html(
        """
Got issue ah? Don't worry, Auntie is here to help you!

Here's what I can do:
1) /check location1 to location2 - to check the prices
2) /add location1 to location2 - to add your specificied route to bookmarks
3) /list - to list your bookmarked routes
4) /remove number - to remove specified bookmark
5) /cancel - to stop whatever you're currently doing
6) /help - for troubleshooting
7) /feedback - to provide any feedback on our bot

Frequently Asked Questions:
Q: There are a lot of similar locations listed. How do I select which one?
A: Some places have multiple pickup point. Inputting a more specific location/postal code will display the most precise results.

Q: How do I remove a bookmark?
A: The bookmarks you saved are listed in the /list command. The first number is the bookmark id. So, if you wish to remove bookmark number 2, type /remove 2
                                    """
    )

    return START_ROUTES
