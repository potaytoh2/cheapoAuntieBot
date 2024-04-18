from telegram.ext import (
    ContextTypes,
)
from telegram import Update

START_ROUTES,SELECT_START_LOCATION,SELECT_END_LOCATION = range(3)
# # Callback data
ONE, TWO, THREE, FOUR = range(4)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Operation cancelled")
    return START_ROUTES
