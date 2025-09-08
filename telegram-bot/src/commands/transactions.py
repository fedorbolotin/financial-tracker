import logging
from telegram import Update
from telegram.ext import ContextTypes

from config.settings import get_credentials
from models.transaction import Transaction
from models.transaction_repository import TransactionRepository
from models.user_repository import UserRepository
from utils.db import Postgres


cred = get_credentials()


async def handle_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle transaction messages from users"""
    db = Postgres(credentials=cred)
    user_repo = UserRepository(db)
    txn_repo = TransactionRepository(db)
    
    try:
        logging.info(f"Update object: {update}")
        logging.info(f"Message: {update.message}")
        logging.info(f"From user: {update.message.from_user}")
        
        chat_id = update.effective_chat.id
        
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
            
        user_row = user_repo.get_by_telegram(username)
        
        if not user_row:
            await context.bot.send_message(
                chat_id=chat_id,
                text='Please sign up first using /signup command'
            )
            return

        default_currency = user_row['default_currency_code']
        transaction = Transaction.from_message(update.message.text, default_currency=default_currency)
        if not transaction:
            await context.bot.send_message(
                chat_id=chat_id,
                text='Invalid format. Use: [date] amount [currency_code] category\n'
                     'Examples:\n'
                     '25.03.2024 100 USD Groceries\n'
                     '100 food (uses your default currency)'
            )
            return

        transaction.user_uuid = user_row['user_uuid']
        
        if txn_repo.insert(transaction):
            await context.bot.send_message(
                chat_id=chat_id,
                text=f'Transaction saved successfully!\n'
                     f'Amount: {transaction.amount_lcy} {transaction.currency_code}\n'
                     f'Category: {transaction.category}\n'
                     f'Date: {transaction.lcl_dttm.strftime("%Y-%m-%d %H:%M:%S")}'
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


