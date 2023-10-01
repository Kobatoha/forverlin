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
from DataBase.Transaction import Transaction
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


# [GET WALLET ADDRESS]
async def get_wallet_address(callback_query: types.CallbackQuery):
    try:
        wallet_address = callback_query.data.split('_')[2]

        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню',
                                                 callback_data=f'wallet_{wallet_address}')
        reply_markup = types.InlineKeyboardMarkup()
        reply_markup.add(back_button)

        text = f'{wallet_address}'
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

    except Exception as e:
        logging.error(f' [GET WALLET ADDRESS] {callback_query.from_user.id} - Ошибка в функции get_wallet_address: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[GET WALLET ADDRESS] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции get_wallet_address: {e}')
