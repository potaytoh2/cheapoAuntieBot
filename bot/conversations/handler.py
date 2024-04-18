from bot.conversations.check import check, handle_start_live_location, on_send_end_location, select_end_live_location
from bot.conversations.add import add
from bot.conversations.cancel import cancel
from bot.conversations.check import select_end_location, select_start_location
from bot.conversations.convo import handle_convo
from bot.conversations.list import listBookmarks
from bot.conversations.save import save, save_to_bookmarks
from bot.conversations.start import start
from bot.conversations.start import button_click
from bot.conversations.help import help
from bot.conversations.remove import remove
from bot.conversations.feedback import feedback
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

START_ROUTES, SELECT_START_LOCATION, SELECT_END_LOCATION = range(3)
# # Callback data
THREE, FOUR, FIVE, SIX, SEVEN, EIGHT = range(3, 9)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start),
                  CallbackQueryHandler(button_click, pattern="^accept$"),],
    states={
        START_ROUTES: [
            CallbackQueryHandler(save_to_bookmarks, pattern="^save_bookmark$"),
            CommandHandler("check", check),
            CommandHandler("add", add),
            CommandHandler("feedback", feedback),
            CommandHandler("list", listBookmarks),
            CommandHandler("help", help),
            CommandHandler("remove", remove),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_convo),
            MessageHandler(filters.LOCATION, handle_start_live_location)
        ],
        SELECT_START_LOCATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, select_start_location)
        ],
        SELECT_END_LOCATION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, select_end_location)
        ],
        THREE: [
            MessageHandler(filters.LOCATION, select_end_live_location),
            MessageHandler(filters.TEXT, on_send_end_location)
        ]

    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
