from bot.conversations.bookmark import handle_numeric_command
from bot.conversations.handler import conv_handler
from dotenv import dotenv_values
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
)

class CheapoAuntieBot:
    def run(self):
        config = dotenv_values(".env")
        telegram_token = config["TELEGRAM_TOKEN"]

        application = (
            Application.builder()
            .token(telegram_token)
            .read_timeout(30)
            .write_timeout(30)
            .build()
        )

        application.add_handler(conv_handler)
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^/\d+$'), handle_numeric_command))
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        application.run_polling()
    