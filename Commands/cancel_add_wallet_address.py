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


class WalletRegistration(StatesGroup):
    waiting_for_wallet_id = State()


# [CANCEL ADD WALLET ADDRESS]
async def cancel_add_wallet_address(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        register_button = types.InlineKeyboardButton(text='Регистрация кошелька', callback_data='register')
        my_wallets_button = types.InlineKeyboardButton(text='Мои кошельки', callback_data='mywallets')
        menu_buttons = types.InlineKeyboardMarkup(row_width=2).add(register_button, my_wallets_button)

        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(chat_id=callback_query.from_user.id, text='Регистрация кошелька отменена',
                               reply_markup=menu_buttons)
        await state.finish()

    except Exception as e:
        logging.error(f' [CANCEL ADD WALLET ADDRESS] {callback_query.from_user.id} - '
                      f'ошибка в функции cancel_add_wallet_address: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[CANCEL ADD WALLET ADDRESS] {callback_query.from_user.id} - '
                                    f'произошла ошибка в функции cancel_add_wallet_address:'
                                    f' {e}')
