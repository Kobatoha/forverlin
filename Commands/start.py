from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, DB_URL
from parser import parser_main
import json
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from DataBase.TransactionWatchWallet import TransactionWatchWallet
from DataBase.TrustedUser import TrustedUser
from DataBase.WalletTron import WalletTron
from DataBase.WatchWallet import WatchWallet
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


# [START]
async def start(message: types.Message):
    try:
        wallet_button = types.KeyboardButton('Кошелек')
        one_button = types.KeyboardButton('One')
        two_button = types.KeyboardButton('Two')
        three_button = types.KeyboardButton('Three')
        start_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).\
            add(wallet_button, one_button, two_button, three_button)

        start_text = f'Привет, это тестовый бот\n'

        await bot.send_message(chat_id=message.from_user.id,
                               text=start_text,
                               reply_markup=start_keyboard)

        session = Session()
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        session.close()

        if user:
            menu_buttons = types.InlineKeyboardMarkup(row_width=2)
            register_button = types.InlineKeyboardButton(text='Регистрация кошелька', callback_data='register')
            my_wallets_button = types.InlineKeyboardButton(text='Мои кошельки', callback_data='mywallets')
            menu_buttons.add(register_button, my_wallets_button)

            comeback_text = f'Добро пожаловать!\n' \
                            f'\n' \
                            f'Ваш аккаунт:\n' \
                            f'ID аккаунта: {user.telegram_id}\n' \
                            f'Дата создания: {user.reg_date}'

            await bot.send_message(chat_id=message.from_user.id,
                                   text=comeback_text,
                                   reply_markup=menu_buttons)
        else:
            register_button = types.InlineKeyboardButton(text='Регистрация кошелька', callback_data='register')
            menu_register = types.InlineKeyboardMarkup()
            menu_register.add(register_button)

            session = Session()
            new_user = User(telegram_id=message.from_user.id, username=message.from_user.username)
            session.add(new_user)
            session.commit()
            session.close()

            welcome_text = f'Добро пожаловать!\n' \
                           f'\n' \
                           f'Ваш аккаунт успешно создан.\n' \
                           f'ID аккаунта: {message.from_user.id}\n' \
                           f'Дата создания: {datetime.today().strftime("%Y-%m-%d %H:%M")}'

            await bot.send_message(chat_id=message.from_user.id,
                                   text=welcome_text,
                                   reply_markup=menu_register)

    except Exception as e:
        logging.error(f'{message.from_user.id} - ошибка в функции start: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[START] {message.from_user.id} - Произошла ошибка в функции start: {e}')
