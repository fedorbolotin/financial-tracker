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
from transaction import Transaction

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

    def insert_transaction(self, transaction: Transaction) -> bool:
        """Insert a transaction into the database"""
        try:
            insert_query = text("""
                INSERT INTO transactions (
                    transaction_id, lcl_dttm, entity_type, category,
                    user_uuid, amount_lcy, currency_code, place,
                    description, expected_transaction_id
                ) VALUES (
                    :transaction_id, :lcl_dttm, :entity_type, :category,
                    :user_uuid, :amount_lcy, :currency_code, :place,
                    :description, :expected_transaction_id
                )
            """)
            
            with self.engine.connect() as connection:
                connection.execute(insert_query, transaction.to_dict())
                connection.commit()
            return True
        except Exception as e:
            logging.error(f"Error inserting transaction: {str(e)}")
            return False

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

async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle transaction messages from users"""
    db = Postgres(credentials=cred)
    
    # Get user info using a more reliable method
    try:
        # Log the update object for debugging
        logging.info(f"Update object: {update}")
        logging.info(f"Message: {update.message}")
        logging.info(f"From user: {update.message.from_user}")
        
        # Get the chat ID which is always available
        chat_id = update.effective_chat.id
        
        # Try to get username from different possible locations
        username = None
        if update.message and update.message.from_user:
            username = update.message.from_user.username
        elif update.effective_user:
            username = update.effective_user.username
            
        if not username:
            await context.bot.send_message(
                chat_id=chat_id,
                text='Sorry, I could not identify you. Please make sure you have a username set in Telegram.'
            )
            return
            
        user_df = db.read_sql(f"SELECT user_uuid, default_currency_code FROM users WHERE telegram_account = '{username}'")
        
        if user_df.shape[0] == 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text='Please sign up first using /signup command'
            )
            return

        # Parse transaction
        transaction = Transaction()
        default_currency = user_df.iloc[0]['default_currency_code']
        
        if not transaction.parse_from_message(update.message.text, default_currency=default_currency):
            await context.bot.send_message(
                chat_id=chat_id,
                text='Invalid transaction format. Please use format: [date] amount [currency_code] place\n'
                     'Examples:\n'
                     '25.03.2024 100 USD Starbucks\n'
                     '100 Starbucks (using your default currency)'
            )
            return

        # Set user UUID
        transaction.user_uuid = user_df.iloc[0]['user_uuid']
        
        # Save transaction
        if db.insert_transaction(transaction):
            await context.bot.send_message(
                chat_id=chat_id,
                text=f'Transaction saved successfully!\n'
                     f'Amount: {transaction.amount_lcy} {transaction.currency_code}\n'
                     f'Place: {transaction.place}\n'
                     f'Date: {transaction.lcl_dttm.strftime("%Y-%m-%d %H:%M:%S")}\n'
                     f'Description: {transaction.description or "N/A"}'
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text='Sorry, there was an error saving your transaction. Please try again later.'
            )
    except Exception as e:
        logging.error(f"Error in handle_transaction: {str(e)}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Sorry, there was an error processing your transaction. Please try again later.'
        )

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
    transaction_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction)
    
    application.add_handler(start_handler)
    application.add_handler(signup_conv_handler)
    application.add_handler(transaction_handler)
    
    logging.info('Starting polling')
    application.run_polling()

