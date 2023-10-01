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


# [DELETE TRUSTED USER] @dp.callback_query_handler(lambda c: c.data.startswith('remove_'))
async def remove_user(callback_query: types.CallbackQuery):
    try:
        data = callback_query.data.split('_')
        wallet_address = data[1]
        username = data[2]

        session = Session()
        trusted_user = session.query(TrustedUser).filter_by(username=username, wallet_address=wallet_address).first()
        session.delete(trusted_user)
        session.commit()
        session.close()

        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню',
                                                 callback_data=f'trusted_users_{wallet_address}')
        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(back_button)

        text = f'Пользователь {trusted_user.username} удален из списка пользователей, ' \
               f'следящих за транзакциями в кошельке {trusted_user.wallet_address}'

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)
    except MessageNotModified:
        pass
    except MessageToDeleteNotFound:
        await bot.send_message(chat_id=callback_query.from_user.id, text=text, reply_markup=reply_markup)

        await bot.answer_callback_query(callback_query_id=callback_query.id)

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции remove_user: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{callback_query.from_user.id} - Произошла ошибка в функции '
                                    f'remove_user: {e}')
