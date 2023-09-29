from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, DB_URL
from sqlalchemy import create_engine, join, or_
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from DataBase.TrustedUser import TrustedUser
from DataBase.WalletTron import WalletTron
from DataBase.WatchWallet import WatchWallet
from DataBase.TransactionWatchWallet import TransactionWatchWallet
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


class ShareWallet(StatesGroup):
    waiting_for_trusted_username = State()


# [SHARE WALLET]
async def share_wallet(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        wallet_address = callback_query.data.split('_')[1]

        session = Session()
        wallet_name = session.query(WatchWallet.wallet_name).filter_by(wallet_address=wallet_address).scalar()
        wallet_tron_name = session.query(WalletTron.wallet_name).filter_by(wallet_address=wallet_address).scalar()
        session.close()

        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню',
                                                 callback_data=f'cancel_to_share_wallet_{wallet_address}')
        reply_markup = types.InlineKeyboardMarkup()
        reply_markup.add(back_button)

        if wallet_name:
            text = f'Введите пользователя (@username), который будет получать уведомления с ' \
                   f'кошелька: «{wallet_name}» - {wallet_address[:3]}...{wallet_address[-3:]}:'
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=reply_markup)
        elif wallet_tron_name:
            text = f'Введите пользователя (@username), который будет получать уведомления с ' \
                   f'кошелька: «{wallet_tron_name}» - {wallet_address[:3]}...{wallet_address[-3:]}:'
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=reply_markup)

        await ShareWallet.waiting_for_trusted_username.set()
        await state.update_data(wallet_address=wallet_address)

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции share_wallet: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{callback_query.from_user.id} - Произошла ошибка в функции share_wallet:'
                                    f' {e}')


# [CANCEL SHARE WALLET] @dp.callback_query_handler(lambda c: c.data.startswith('cancel_to_share_wallet_'
# '', state=ShareWallet.waiting_for_trusted_username)
async def cancel_to_share_wallet(callback_query: types.CallbackQuery, state: FSMContext):
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
        wallet_name = session.query(WatchWallet.wallet_name).filter_by(wallet_address=wallet_address).scalar()
        wallet_tron_name = session.query(WalletTron.wallet_name).filter_by(wallet_address=wallet_address).scalar()
        session.close()
        if wallet_name:
            text = f'Выберите действие с кошельком «{wallet_name}» - {wallet_address}:'
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=reply_markup)
        elif wallet_tron_name:
            text = f'Выберите действие с кошельком «{wallet_tron_name}» - {wallet_address}:'
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=reply_markup)

        await state.finish()

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции cancel_to_share_wallet: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции cancel_to_share_wallet: {e}')