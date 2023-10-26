import json
import uuid
import datetime
import logging
import psycopg2 as pg
import pandas as pd

from os.path import expanduser
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from sqlalchemy import create_engine, URL

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
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Greetings human, to sign-up use /singup command')
    else:
        await context.bot.send_message(chat_id = update.effective_chat.id, text = 'Greetings human, you are signed up and ready to go!')

async def signup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return None

if __name__ == '__main__':
    application = ApplicationBuilder().token(cred['tg_bot_token']).build()
    logging.info('Application started')
    
    start_handler = CommandHandler('start', start_command)
    application.add_handler(start_handler)

    signup_handler = CommandHandler('signup', signup_command)
    application.add_handler(signup_handler)
    
    logging.info('Starting polling')
    application.run_polling()

