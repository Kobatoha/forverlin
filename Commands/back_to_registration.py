from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, DB_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from DataBase.TrustedUser import TrustedUser
from DataBase.WalletTron import WalletTron
from DataBase.WatchWallet import WatchWallet
from DataBase.TransactionWatchWallet import TransactionWatchWallet
from datetime import datetime
from aiocron import crontab
import asyncio
import logging


logging.basicConfig(filename='bot.log', level=logging.INFO)

engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

menu_buttons = types.InlineKeyboardMarkup(row_width=2)
register_button = types.InlineKeyboardButton(text='Регистрация кошелька', callback_data='register')
my_wallets_button = types.InlineKeyboardButton(text='Мои кошельки', callback_data='mywallets')
menu_buttons.add(register_button, my_wallets_button)


# [BACK TO REGISTRATION]
async def back_to_registration(callback_query: types.CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id)
        text = '[Регистрация кошелька] - Добавьте свой адрес\n' \
               '[Мои кошельки] - Измените существующий или создайте новый'
        reply_markup = menu_buttons
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции back_to_registration: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[BACK TO REGISTRATION] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции back_to_registration: {e}')
