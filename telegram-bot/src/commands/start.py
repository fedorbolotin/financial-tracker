import logging
from telegram import Update
from telegram.ext import ContextTypes

from utils.db import Postgres
from config.settings import get_credentials


cred = get_credentials()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = Postgres(credentials=cred)
    logging.info(update.message.from_user.username)
    df = db.fetch_df(
        "SELECT 1 FROM users WHERE telegram_account = :username",
        {"username": update.message.from_user.username}
    )
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


