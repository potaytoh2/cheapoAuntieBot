
from bot.conversations.save import save
from telegram.ext import (
    ContextTypes,
    CallbackContext,
)
from telegram import Update

START_ROUTES, SELECT_START_LOCATION, SELECT_END_LOCATION = range(3)
# # Callback data
ONE, TWO, THREE, FOUR = range(4)


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_html(
        """
    Hi, we greatly appreciate any feedback! Please send your feedback here

    "https://forms.gle/ZHDADNyqAPQBjdWD9"
                                    """
    )

    return START_ROUTES
