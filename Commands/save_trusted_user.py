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


class ShareWallet(StatesGroup):
    waiting_for_trusted_username = State()


# [SAVE TRUSTED USER]
async def save_trusted_user(message: types.Message, state: FSMContext):
    try:
        trusted_username = message.text

        if not trusted_username.startswith('@'):
            await message.reply('Имя пользователя должно начинаться с символа @. Попробуйте еще раз:')
            return

        data = await state.get_data()
        wallet_address = data.get('wallet_address')

        session = Session()
        trusted_user = session.query(TrustedUser).filter_by(wallet_address=wallet_address).first()

        if trusted_user and trusted_user.username == trusted_username:
            await message.reply('Пользователь уже следит за этим кошельком. Повторите попытку или вернитесь назад.')
            return

        session.close()

        trusted_user = TrustedUser(username=trusted_username, wallet_address=wallet_address)
        session.add(trusted_user)
        session.commit()
        session.close()

        session = Session()
        wallet_name = session.query(WatchWallet.wallet_name).filter_by(wallet_address=wallet_address).scalar()
        wallet_tron_name = session.query(WalletTron.wallet_name).filter_by(wallet_address=wallet_address).scalar()
        session.close()

        buttons = [
            types.InlineKeyboardButton(text='Добавить пользователя', callback_data=f'share_{wallet_address}'),
            types.InlineKeyboardButton(text='Удалить пользователя', callback_data=f'remove_{wallet_address}'),
            types.InlineKeyboardButton(text='Вернуться в предыдущее меню', callback_data=f'wallet_{wallet_address}')
        ]

        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(*buttons)

        if wallet_name:
            text = f'Пользователь «{trusted_username}» добавлен для слежения за транзакциями в кошельке ' \
                   f'«{wallet_name}» - {wallet_address[:3]}...{wallet_address[-3:]}.\n' \
                   f'Чтобы пользователь «{trusted_username}» получал уведомления о новых транзакциях, ' \
                   f'отправьте ему ссылку на бота, чтобы он авторизовался нажатием на кнопку start'

            await bot.send_message(chat_id=message.from_user.id,
                                   text=text,
                                   reply_markup=reply_markup)
            await bot.send_message(chat_id=message.from_user.id,
                                   text='https://t.me/NonameKobatohaBot')

        elif wallet_tron_name:
            text = f'Пользователь «{trusted_username}» добавлен для слежения за транзакциями в кошельке ' \
                   f'«{wallet_tron_name}» - {wallet_address[:3]}...{wallet_address[-3:]}.\n' \
                   f'Чтобы пользователь «{trusted_username}» получал уведомления о новых транзакциях, ' \
                   f'отправьте ему ссылку на бота, чтобы он авторизовался нажатием на кнопку start'

            await bot.send_message(chat_id=message.from_user.id,
                                   text='https://t.me/NonameKobatohaBot')

            await bot.send_message(chat_id=message.from_user.id,
                                   text=text,
                                   reply_markup=reply_markup)

        await state.finish()

    except Exception as e:
        logging.error(f'{message.from_user.id} - Ошибка в функции save_trusted_user: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{message.from_user.id} - Произошла ошибка в функции '
                                    f'save_trusted_user: {e}')
