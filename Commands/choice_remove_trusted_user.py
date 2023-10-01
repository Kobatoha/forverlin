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


# [CHOICE REMOVE TRUSTED USER]
async def choice_remove_trusted_user(callback_query: types.CallbackQuery):
    try:
        wallet_address = callback_query.data.split('_')[3]

        text = f'Какого пользователя вы желаете отключить от уведомлений «{wallet_address}»?'
        reply_markup = types.InlineKeyboardMarkup(row_width=1)

        session = Session()
        trusted_users = session.query(TrustedUser).filter_by(wallet_address=wallet_address).all()
        session.close()

        buttons = []
        for trusted_user in trusted_users:
            buttons.append(types.InlineKeyboardButton(text=f'Отключить «{trusted_user.username}»',
                                                      callback_data=f'remove_{wallet_address}_{trusted_user.username}'))

        buttons.append(types.InlineKeyboardButton(text='Вернуться в предыдущее меню',
                                                  callback_data=f'trusted_users_{wallet_address}'))
        reply_markup.add(*buttons)

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)
    except MessageNotModified:
        pass
    except MessageToDeleteNotFound:
        await bot.send_message(chat_id=callback_query.from_user.id, text=text, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f' [CHOICE REMOVE TRUSTED USER] {callback_query.from_user.id} - '
                      f'Ошибка в функции choice_remove_trusted_user: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[CHOICE REMOVE TRUSTED USER]{callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции choice_remove_trusted_user: {e}')
