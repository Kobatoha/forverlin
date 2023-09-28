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


inline_register_buttons = types.InlineKeyboardMarkup()
button_yes = types.InlineKeyboardButton(text='Введите адрес', callback_data='insert_wallet_id')
button_no = types.InlineKeyboardButton(text='« back', callback_data='back_to_reg')
inline_register_buttons.add(button_yes, button_no)

menu_buttons = types.InlineKeyboardMarkup(row_width=2)
register_button = types.InlineKeyboardButton(text='Регистрация кошелька', callback_data='register')
my_wallets_button = types.InlineKeyboardButton(text='Мои кошельки', callback_data='mywallets')
menu_buttons.add(register_button, my_wallets_button)

menu_register = types.InlineKeyboardMarkup()
menu_register.add(register_button)


# [START REGISTER]
async def start_register(callback_query: types.CallbackQuery):
    try:
        session = Session()
        user = session.query(WatchWallet).filter_by(telegram_id=callback_query.from_user.id).\
            order_by(WatchWallet.id.desc()).first()

        if not user or (user and user.wallet_address):

            user = WatchWallet(telegram_id=callback_query.from_user.id, username=callback_query.from_user.username)
            session.add(user)
            session.commit()

            session.close()

            text = 'Вы можете добавить адрес своего кошелька для отслеживания поступлений'

            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=inline_register_buttons)

        elif user and not user.wallet_address:

            text = 'Вы можете добавить адрес своего кошелька для отслеживания поступлений'

            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=inline_register_buttons)

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - ошибка в функции start_register: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[START REGISTER] {callback_query.from_user.id} - '
                                    f'ошибка Произошла ошибка в функции START REGISTER:'
                                    f' {e}')


# [ADD WALLET ID AND WALLET NAME]
async def insert_wallet_id(callback_query: types.CallbackQuery):
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='Пожалуйста, введите адрес своего кошелька:')

        await WalletRegistration.waiting_for_wallet_id.set()
        # добавляем кнопку "назад"
        back_button = types.InlineKeyboardButton('<< back', callback_data='cancel_to_register')
        keyboard = types.InlineKeyboardMarkup().add(back_button)

        await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                            reply_markup=keyboard)

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - ошибка в функции insert_wallet_id: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[ADD WALLET ID AND WALLET NAME] {callback_query.from_user.id} - '
                                    f'произошла ошибка в функции insert_wallet_id: {e}')


# [CANCEL TO REGISTER WALLET ID]
async def cancel_to_register(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(chat_id=callback_query.from_user.id, text='Регистрация кошелька отменена',
                               reply_markup=menu_buttons)
        await state.finish()

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - ошибка в функции cancel_to_register: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[CANCEL TO REGISTER WALLET ID] {callback_query.from_user.id} - '
                                    f'произошла ошибка в функции cancel_to_register:'
                                    f' {e}')


# [SAVE WALLET ID]
async def save_wallet_id(message: types.Message, state: FSMContext):
    try:

        wallet_id = message.text
        session = Session()
        user = session.query(WatchWallet).filter_by(telegram_id=message.from_user.id).\
            order_by(WatchWallet.id.desc()).first()

        if len(wallet_id) != 34 or not wallet_id.isalnum() or wallet_id.isupper():

            await bot.send_message(chat_id=message.from_user.id,
                                   text='Некорректный формат, попробуйте еще раз.')
            return

        elif session.query(WatchWallet).filter_by(wallet_address=wallet_id).first():

            await bot.send_message(chat_id=message.from_user.id,
                                   text='Такой адрес уже зарегистрирован в системе. Попробуйте еще раз.')
            return

        user.wallet_address = wallet_id
        session.commit()

        wallet_count = session.query(WatchWallet).filter_by(telegram_id=message.from_user.id).count()

        user.wallet_name = f'wallet {wallet_count}'
        session.commit()

        session.close()

        await bot.send_message(chat_id=message.from_user.id,
                               text='Вы успешно добавили адрес. Вы можете добавить новый адрес или '
                                    'изменить существующий',
                               reply_markup=menu_buttons)

        await state.finish()

    except Exception as e:
        logging.error(f'{message.from_user.id} - ошибка в функции save_wallet_id: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[SAVE WALLET ID] {message.from_user.id} - '
                                    f'произошла ошибка в функции save_wallet_id: {e}')
