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


class WalletNameEdit(StatesGroup):
    waiting_for_new_name = State()


# [CANCEL EDIT WALLET NAME]
async def cancel_edit_wallet_name(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        wallet_address = callback_query.data.split('_')[4]
        buttons = [
            types.InlineKeyboardButton(text='Получить адрес', callback_data=f'get_address_{wallet_address}'),
            types.InlineKeyboardButton(text='Редактировать название', callback_data=f'edit_{wallet_address}'),
            types.InlineKeyboardButton(text='Удалить', callback_data=f'delete_{wallet_address}'),
            types.InlineKeyboardButton(text='Поделиться', callback_data=f'share_{wallet_address}'),
            types.InlineKeyboardButton(text='Доверенные пользователи', callback_data=f'trusted_users_{wallet_address}')
        ]
        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню', callback_data='mywallets')
        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(*buttons, back_button)

        session = Session()
        wallet_name = session.query(WalletTron.wallet_name).filter_by(wallet_address=wallet_address).scalar()
        session.close()

        if wallet_name:
            text = f'Выберите действие с кошельком «{wallet_name}» - «{wallet_address}»:'
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=reply_markup)

        await state.finish()

    except Exception as e:
        logging.error(f' [CANCEL EDIT WALLET NAME] {callback_query.from_user.id} - '
                      f'Ошибка в функции cancel_edit_wallet_name: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[CANCEL EDIT WALLET NAME] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции cancel_edit_wallet_name: {e}')
