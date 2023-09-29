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


# [SAVE WALLET NAME]
@dp.message_handler(state=WalletNameEdit.waiting_for_new_name)
async def save_wallet_name(message: types.Message, state: FSMContext):
    try:
        new_wallet_name = message.text
        data = await state.get_data()
        wallet_address = data.get('wallet_address')

        session = Session()
        watch_wallet = session.query(WatchWallet).filter_by(wallet_address=wallet_address).first()
        if watch_wallet:
            watch_wallet.wallet_name = new_wallet_name.strip()
            session.commit()

        else:
            tron_wallet = session.query(WalletTron).filter_by(wallet_address=wallet_address).first()
            tron_wallet.wallet_name = new_wallet_name.strip()
            session.commit()
        session.close()

        buttons = [
            types.InlineKeyboardButton(text='Получить адрес', callback_data=f'get_address_{wallet_address}'),
            types.InlineKeyboardButton(text='Редактировать название', callback_data=f'edit_{wallet_address}'),
            types.InlineKeyboardButton(text='Удалить', callback_data=f'delete_{wallet_address}'),
            types.InlineKeyboardButton(text='Поделиться', callback_data=f'share_{wallet_address}'),
            types.InlineKeyboardButton(text='Доверенные пользователи', callback_data=f'trusted_users_{wallet_address}')
        ]

        back_button = types.InlineKeyboardButton(text='Вернуться в предыдущее меню',
                                                 callback_data=f'wallet_{wallet_address}')
        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(*buttons, back_button)

        text = f'Выберите действие с кошельком "{new_wallet_name}" - "{wallet_address}":'
        await bot.send_message(chat_id=message.from_user.id,
                               text=text,
                               reply_markup=reply_markup)

        await state.finish()

    except Exception as e:
        logging.error(f'{message.from_user.id} - Ошибка в функции save_wallet_name: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{message.from_user.id} - Произошла ошибка в функции save_wallet_name:'
                                    f' {e}')
