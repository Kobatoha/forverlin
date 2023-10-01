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


menu_buttons = types.InlineKeyboardMarkup(row_width=2)
register_button = types.InlineKeyboardButton(text='Регистрация кошелька', callback_data='register')
my_wallets_button = types.InlineKeyboardButton(text='Мои кошельки', callback_data='mywallets')
menu_buttons.add(register_button, my_wallets_button)


# [SAVE WALLET ADDRESS]
async def save_wallet_address(message: types.Message, state: FSMContext):
    try:
        wallet_address = message.text
        session = Session()

        if len(wallet_address) != 34 or not wallet_address.isalnum() or wallet_address.isupper():

            await bot.send_message(chat_id=message.from_user.id,
                                   text='Некорректный формат, попробуйте еще раз.')
            return

        elif session.query(WalletTron).filter_by(wallet_address=wallet_address).first():

            await bot.send_message(chat_id=message.from_user.id,
                                   text='Такой адрес уже зарегистрирован в системе. Попробуйте еще раз.')
            return

        wallet = WalletTron(telegram_id=message.from_user.id,
                            wallet_address=wallet_address,
                            only_watch=True)
        session.add(wallet)
        session.commit()

        wallet_count = session.query(WalletTron).filter_by(telegram_id=message.from_user.id).count()

        wallet.wallet_name = f'wallet {wallet_count}'
        session.commit()

        session.close()

        await bot.send_message(chat_id=message.from_user.id,
                               text='Вы успешно добавили адрес. Вы можете добавить новый адрес или '
                                    'изменить существующий',
                               reply_markup=menu_buttons)

        await state.finish()

    except Exception as e:
        logging.error(f' [SAVE WALLET ADDRESS] {message.from_user.id} - ошибка в функции save_wallet_address: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[SAVE WALLET ADDRESS] {message.from_user.id} - '
                                    f'произошла ошибка в функции save_wallet_address: {e}')
