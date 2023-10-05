from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, DB_URL
import json
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.WalletTron import WalletTron
from datetime import datetime
from aiocron import crontab
import asyncio
import logging


logging.basicConfig(filename='../bot.log', level=logging.INFO)

engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# [CONFIRM CREATE TRON WALLET]
async def confirm_create_tron_wallet(callback_query: types.CallbackQuery):
    try:
        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню', callback_data='mywallets')
        confirm_button = types.InlineKeyboardButton(text='Подтвердить', callback_data='create_tron_wallet')
        reply_markup = types.InlineKeyboardMarkup(row_width=1).add(confirm_button, back_button)

        text = f'Вы подтверждаете создание адреса?'

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

    except Exception as e:
        logging.error(f' [CONFIRM CREATE TRON WALLET] {callback_query.from_user.id} - '
                      f'ошибка в функции confirm_create_tron_wallet: {e}')
        await mybot.send_message(chat_id='952604184',
                                 text=f'[CONFIRM CREATE TRON WALLET] {callback_query.from_user.id} - '
                                      f'Произошла ошибка в функции confirm_create_tron_wallet: {e}')
