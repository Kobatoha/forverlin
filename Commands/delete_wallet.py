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


# [DELETE WALLET]
async def delete_wallet(callback_query: types.CallbackQuery):
    try:
        wallet_address = callback_query.data.split('_')[1]

        session = Session()
        session.query(Transaction).filter_by(wallet_address=wallet_address).delete()
        session.query(TrustedUser).filter_by(wallet_address=wallet_address).delete()
        session.query(WalletTron).filter_by(wallet_address=wallet_address).delete()
        session.commit()
        session.close()

        text = 'Кошелек успешно удален!\n' \
               '\n' \
               '[Регистрация кошелька] - Добавьте свой адрес\n' \
               '[Мои кошельки] - Измените существующий или создайте новый'

        reply_markup = menu_buttons
        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

    except Exception as e:
        logging.error(f' [DELETE WALLET] {callback_query.from_user.id} - Ошибка в функции delete_wallet: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[DELETE WALLET] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции delete_wallet: {e}')
