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


class WalletNameEdit(StatesGroup):
    waiting_for_new_name = State()


# [EDIT WALLET NAME]
async def edit_wallet_name(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        wallet_address = callback_query.data.split('_')[1]

        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню',
                                                 callback_data=f'cancel_edit_wallet_name_{wallet_address}')
        reply_markup = types.InlineKeyboardMarkup()
        reply_markup.add(back_button)

        text = f'Введите новое название для кошелька «{wallet_address}»:'
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

        await WalletNameEdit.waiting_for_new_name.set()
        await state.update_data(wallet_address=wallet_address)

    except Exception as e:
        logging.error(f' [EDIT WALLET NAME] {callback_query.from_user.id} - Ошибка в функции edit_wallet_name: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[EDIT WALLET NAME] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции edit_wallet_name: {e}')
