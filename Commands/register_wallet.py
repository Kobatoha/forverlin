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
from DataBase.Transaction import TransactionWatchWallet
from datetime import datetime
import asyncio
import logging

logging.basicConfig(filename='bot.log', level=logging.INFO)

engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# [REGISTER WALLET]
async def register_wallet(callback_query: types.CallbackQuery):
    try:
        inline_register_buttons = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton(text='Введите адрес', callback_data='add_wallet_address')
        button_no = types.InlineKeyboardButton(text='Вернуться в предыдущее меню', callback_data='back_to_registration')
        inline_register_buttons.add(button_yes, button_no)

        text = 'Вы можете добавить адрес своего кошелька для отслеживания поступлений'

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=inline_register_buttons)

    except Exception as e:
        logging.error(f'[REGISTER WALLET] {callback_query.from_user.id} - ошибка в функции start_register: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[REGISTER WALLET] {callback_query.from_user.id} - '
                                    f'ошибка Произошла ошибка в функции START REGISTER:'
                                    f' {e}')
