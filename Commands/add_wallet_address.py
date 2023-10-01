from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, DB_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
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


class WalletRegistration(StatesGroup):
    waiting_for_wallet_id = State()


# [ADD WALLET ADDRESS]
async def add_wallet_address(callback_query: types.CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='Пожалуйста, введите адрес своего кошелька:')

        await WalletRegistration.waiting_for_wallet_id.set()

        back_button = types.InlineKeyboardButton('Вернуться в предыдущее меню',
                                                 callback_data='cancel_add_wallet_address')
        keyboard = types.InlineKeyboardMarkup().add(back_button)

        await bot.edit_message_reply_markup(callback_query.message.chat.id,
                                            callback_query.message.message_id,
                                            reply_markup=keyboard)

    except Exception as e:
        logging.error(f' [ADD WALLET ADDRESS] {callback_query.from_user.id} - ошибка в функции add_wallet_address: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[ADD WALLET ADDRESS] {callback_query.from_user.id} - '
                                    f'произошла ошибка в функции add_wallet_address: {e}')
