from tronpy import Tron
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


# [CREATE TRON WALLET]
async def create_tron_wallet(callback_query: types.CallbackQuery):
    try:
        # подключаемся к блокчейну трон
        client = Tron()
        session = Session()
        # создаем кошелек и печатаем его данные
        new_wallet = client.generate_address()
        print("Create Wallet address:  %s" % new_wallet['base58check_address'])
        print("Create Private Key:  %s" % new_wallet['private_key'])
        wallet = WalletTron(telegram_id=callback_query.from_user.id, wallet_address=new_wallet['base58check_address'],
                            private_key=new_wallet['private_key'], upd_date=datetime.today())

        session.add(wallet)
        session.commit()

        wallet_count = session.query(WalletTron).filter_by(telegram_id=callback_query.from_user.id).count()

        wallet.wallet_name = f'wallet tron {wallet_count}'
        session.commit()

        session.close()

        back_button = types.InlineKeyboardButton(text='« back', callback_data='mywallets')
        reply_markup = types.InlineKeyboardMarkup().add(back_button)

        text = f'Адрес для TRX кошелька:\n' \
               f'Для: Tron\n' \
               f'Минимальный депозит: 00.0'

        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=text)
        text_address = new_wallet['base58check_address']
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=text_address,
                               reply_markup=reply_markup)

    except Exception as e:
        logging.error(f' {callback_query.from_user.id} - ошибка в функции create_wallet: {e}')
        await mybot.send_message(chat_id='952604184',
                                 text=f'[CREATE TRON WALLET] {callback_query.from_user.id} - '
                                      f'Произошла ошибка в функции create_wallet: {e}')
