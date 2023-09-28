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


class WalletNameEdit(StatesGroup):
    waiting_for_new_name = State()


# [EDIT WALLET NAME]
@dp.callback_query_handler(lambda c: c.data.startswith('edit_'))
async def edit_wallet_name(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        wallet_address = callback_query.data.split('_')[1]

        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню',
                                                 callback_data=f'cancel_to_edit_wallet_name_{wallet_address}')
        reply_markup = types.InlineKeyboardMarkup()
        reply_markup.add(back_button)

        text = f'Введите новое название для кошелька {wallet_address}:'
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

        await WalletNameEdit.waiting_for_new_name.set()
        await state.update_data(wallet_address=wallet_address)

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции edit_callback: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{callback_query.from_user.id} - Произошла ошибка в функции edit_callback:'
                                    f' {e}')


# CANCEL FOR CHANGE WALLET NAME
@dp.callback_query_handler(lambda c: c.data.startswith('cancel_to_edit_wallet_name_'),
                           state=WalletNameEdit.waiting_for_new_name)
async def cancel_to_edit_wallet_name(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        wallet_address = callback_query.data.split('_')[5]
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

        # получение названия кошелька из базы данных
        session = Session()
        wallet_name = session.query(WatchWallet.wallet_name).filter_by(wallet_address=wallet_address).scalar()
        wallet_tron_name = session.query(WalletTron.wallet_name).filter_by(wallet_address=wallet_address).scalar()
        session.close()
        if wallet_name:
            text = f'Выберите действие с кошельком "{wallet_name}" - "{wallet_address}":'
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=reply_markup)
        elif wallet_tron_name:
            text = f'Выберите действие с кошельком "{wallet_tron_name}" - "{wallet_address}":'
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=reply_markup)

        await state.finish()

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции cancel_to_edit_wallet_name: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции cancel_to_edit_wallet_name: {e}')
