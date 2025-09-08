import json
import uuid
import datetime
import logging
import os
import psycopg2 as pg
import pandas as pd
import asyncio

from os.path import expanduser
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    Application,
    Defaults
)
from sqlalchemy import create_engine, URL, text

from config.settings import get_credentials, CHOOSING_CURRENCY, VALID_CURRENCIES
from commands.start import start_command
from commands.signup import signup_command, handle_currency_choice, cancel
from commands.transactions import handle_transaction
from utils.db import Postgres

logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

# Get credentials
cred = get_credentials()

### Removed Postgres class from here; using utils.db.Postgres

# Commands moved to commands/ package

if __name__ == '__main__':

    # defaults = Defaults(
    #     block=False,
    #     timeout=30
    # )

    application = (
        ApplicationBuilder()
        .token(cred['tg_bot_token'])
        # .defaults(defaults)
        .get_updates_read_timeout(42)
        .get_updates_write_timeout(42)
        .get_updates_connection_pool_size(1)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    logging.info('Application started')
    
    # Create conversation handler for signup process
    signup_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('signup', signup_command)],
        states={
            CHOOSING_CURRENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_currency_choice)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add handlers
    start_handler = CommandHandler('start', start_command)
    transaction_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction)
    
    application.add_handler(start_handler)
    application.add_handler(signup_conv_handler)
    application.add_handler(transaction_handler)
    
    try:
        logging.info('Starting polling')
        application.run_polling(
            drop_pending_updates=True,  # Ignore updates that arrived while bot was offline
            allowed_updates=["message", "callback_query"],  # Specify which updates to handle
            poll_interval=1.0,  # Time between polling requests
            timeout=30  # How long to wait for response from Telegram
        )
    except Exception as e:
        logging.error(f"Error in main loop: {e}")
        asyncio.sleep(5)

