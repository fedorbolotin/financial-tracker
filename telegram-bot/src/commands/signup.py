import uuid
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from config.settings import CHOOSING_CURRENCY, VALID_CURRENCIES, get_credentials
from models.user_repository import UserRepository
from models.user import User
from utils.db import Postgres


cred = get_credentials()


async def signup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = Postgres(credentials=cred)
    user_repo = UserRepository(db)
    username = update.message.from_user.username
    
    # Check if user already exists
    existing = user_repo.get_by_telegram(username)
    if existing:
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
    user_repo = UserRepository(db)

    new_user = User.from_signup(
        user_uuid=context.user_data['user_uuid'],
        username=context.user_data['username'],
        currency_code=chosen_currency
    )

    inserted = user_repo.insert(new_user)
    if inserted:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Successfully registered! Your default currency is set to {chosen_currency}.',
            reply_markup=ReplyKeyboardRemove()
        )
    else:
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


