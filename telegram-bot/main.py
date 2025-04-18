import json
import uuid
import datetime
import logging
import psycopg2 as pg
import pandas as pd

from os.path import expanduser
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from sqlalchemy import create_engine, URL, text

CHOOSING_CURRENCY = 1
VALID_CURRENCIES = ['EUR', 'USD', 'RUB']

logging.basicConfig(
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level = logging.INFO
)

cred_path = expanduser('~/Documents/Projects/financial-tracker/telegram-bot/credentials.json')
with open(cred_path) as f:
    cred = json.load(f)

class Postgres:
    def __init__(self, credentials) -> None:
        self.cred = credentials
        self._url_object = URL.create(
                        'postgresql+psycopg2'
                        , username = self.cred['pg_user']
                        , password = ''
                        , host = self.cred['pg_host']
                        , database = self.cred['pg_database']
                    )
    
        self.engine = create_engine(self._url_object)

    def read_sql(self, query) -> pd.DataFrame:
        df = pd.read_sql_query(query, self.engine.connect())
        return df
    
    def insert_data(self, query) -> None:
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = Postgres(credentials=cred)
    logging.info(update.message.from_user.username)
    df = db.read_sql(f"select 1 from users where telegram_account = '{update.message.from_user.username}'")
    if df.shape[0] == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text='Greetings human, to sign-up use /signup command'
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text='Greetings human, you are signed up and ready to go!'
        )

async def signup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = Postgres(credentials=cred)
    username = update.message.from_user.username
    
    # Check if user already exists
    df = db.read_sql(f"SELECT 1 FROM users WHERE telegram_account = '{username}'")
    if df.shape[0] > 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='You are already registered!'
        )
        return ConversationHandler.END
    
    # Create keyboard with currency options
    reply_keyboard = [[currency] for currency in VALID_CURRENCIES]
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Please choose your default currency:',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder='Choose currency'
        )
    )
    
    # Store username and generated UUID in context for later use
    context.user_data['user_uuid'] = str(uuid.uuid4())
    context.user_data['username'] = username
    
    return CHOOSING_CURRENCY

async def handle_currency_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chosen_currency = update.message.text
    
    if chosen_currency not in VALID_CURRENCIES:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Please choose a valid currency: {", ".join(VALID_CURRENCIES)}',
            reply_markup=ReplyKeyboardMarkup(
                [[currency] for currency in VALID_CURRENCIES],
                one_time_keyboard=True
            )
        )
        return CHOOSING_CURRENCY
    
    db = Postgres(credentials=cred)
    
    # Insert new user with chosen currency using SQLAlchemy text()
    insert_query = text("""
        INSERT INTO users (user_uuid, telegram_account, default_currency_code)
        VALUES (:user_uuid, :username, :currency)
    """)
    
    try:
        with db.engine.connect() as connection:
            connection.execute(
                insert_query,
                {
                    "user_uuid": context.user_data['user_uuid'],
                    "username": context.user_data['username'],
                    "currency": chosen_currency
                }
            )
            connection.commit()
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Successfully registered! Your default currency is set to {chosen_currency}.',
            reply_markup=ReplyKeyboardRemove()
        )
    except Exception as e:
        logging.error(f"Error during signup: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Sorry, there was an error during registration. Please try again later.',
            reply_markup=ReplyKeyboardRemove()
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Signup cancelled.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(cred['tg_bot_token']).build()
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
    application.add_handler(start_handler)
    application.add_handler(signup_conv_handler)
    
    logging.info('Starting polling')
    application.run_polling()

