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


# [CONFIRM DELETE WALLET]
async def confirm_delete_wallet(callback_query: types.CallbackQuery):
    try:
        wallet_address = callback_query.data.split('_')[2]

        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню', callback_data='mywallets')
        confirm_button = types.InlineKeyboardButton(text='Подтвердить',
                                                    callback_data=f'delete_{wallet_address}')
        reply_markup = types.InlineKeyboardMarkup(row_width=1).add(confirm_button, back_button)

        text = f'Вы подтверждаете удаление адреса?'

        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=text,
                               reply_markup=reply_markup)

    except Exception as e:
        logging.error(f' [CONFIRM DELETE WALLET] {callback_query.from_user.id} - '
                      f'ошибка в функции confirm_delete_wallet: {e}')
        await mybot.send_message(chat_id='952604184',
                                 text=f'[CONFIRM DELETE WALLET] {callback_query.from_user.id} - '
                                      f'Произошла ошибка в функции confirm_delete_wallet: {e}')
