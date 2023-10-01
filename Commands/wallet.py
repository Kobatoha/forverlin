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


# [WALLETS] reply button
async def wallets(message: types.Message):
    try:
        user_id = message.from_user.id

        session = Session()

        wallets_tron = session.query(WalletTron.wallet_address, WalletTron.wallet_name).filter(
            WalletTron.telegram_id == user_id).all()
        session.close()

        buttons = []

        for wallet, wallet_name in wallets_tron:
            button_text = f'{wallet_name} - {wallet[:3]}...{wallet[-3:]}'
            buttons.append(types.InlineKeyboardButton(text=button_text, callback_data=f'wallet_{wallet}'))

        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню',
                                                 callback_data='back_to_registration')
        create_wallet_button = types.InlineKeyboardButton(text='Создать кошелек',
                                                          callback_data='create_tron_wallet')
        session = Session()
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        session.close()
        text = f'Добро пожаловать!\n' \
               f'\n' \
               f'Ваш аккаунт:\n' \
               f'ID аккаунта: {user.telegram_id}\n' \
               f'Дата создания: {user.reg_date}\n' \
               f'\n' \
               f'Ваши кошельки в системе Старого Грузина: '

        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(*buttons, create_wallet_button, back_button)

        await bot.send_message(chat_id=message.from_user.id,
                               text=text,
                               reply_markup=reply_markup)

    except Exception as e:
        logging.error(f' [WALLETS] reply button {message.from_user.id} - Ошибка в функции wallets: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[WALLETS] reply button {message.from_user.id} - '
                                    f'Произошла ошибка в функции wallets: {e}')


# [MY WALLETS] inline button
async def my_wallets(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.from_user.id

        session = Session()
        wallets_tron = session.query(WalletTron.wallet_address, WalletTron.wallet_name).filter(
            WalletTron.telegram_id == user_id).all()
        session.close()

        buttons = []

        for wallet, wallet_name in wallets_tron:
            button_text = f'{wallet_name} - {wallet[:3]}...{wallet[-3:]}'
            buttons.append(types.InlineKeyboardButton(text=button_text, callback_data=f'wallet_{wallet}'))

        create_wallet_button = types.InlineKeyboardButton(text='Создать кошелек', callback_data='create_tron_wallet')
        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню',
                                                 callback_data='back_to_registration')

        session = Session()
        user = session.query(User).filter_by(telegram_id=callback_query.from_user.id).first()
        session.close()
        text = f'Добро пожаловать!\n' \
               f'\n' \
               f'Ваш аккаунт:\n' \
               f'ID аккаунта: {user.telegram_id}\n' \
               f'Дата создания: {user.reg_date}\n' \
               f'\n' \
               f'Ваши кошельки в системе Старого Грузина: '

        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(*buttons, create_wallet_button, back_button)

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)
    except Exception as e:
        logging.error(f' [MY WALLETS] inline button {callback_query.from_user.id} - Ошибка в функции my_wallets: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[MY WALLETS] inline button {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции my_wallets: {e}')
