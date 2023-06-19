from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, LabeledPrice, InlineKeyboardButton,
    InlineKeyboardMarkup, PhotoSize, InputFile
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    ConversationHandler, MessageHandler, StringCommandHandler,
    filters, PreCheckoutQueryHandler, CallbackQueryHandler, CallbackContext,
)
import os
from dotenv import load_dotenv
import logging
import requests

# Loggerdea
logger = logging.getLogger(__name__)

load_dotenv() #important!

TELE_TOKEN_TEST = os.getenv("TELE_TOKEN")
ROUTE, ADD_WALLET,CHECK_RESPONSE = range(3)

async def start(update, context: ContextTypes.DEFAULT_TYPE):

    message = "Hello Stranger, are you ready to begin your defilytics journey?"

    await context.bot.send_message( # I want to store this message so that I can delete it later on
        chat_id=update.effective_chat.id, 
        text=message, 
        parse_mode="markdown", 
    )
    return ROUTE

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry did not understand that command please use /start" 
    )
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELE_TOKEN_TEST).build()

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        fallbacks=[MessageHandler(filters.TEXT, unknown)],
        states = {
            ROUTE: {                
                CallbackQueryHandler(start, pattern="^start$"),
            }})

    application.add_handler(conversation_handler)
    application.run_polling()
    logger.info("Application running via polling")