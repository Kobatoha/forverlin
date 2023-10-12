from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, DB_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from datetime import datetime
import asyncio
import logging


logging.basicConfig(filename='bot.log', level=logging.INFO)

engine = create_engine(DB_URL, pool_size=100, max_overflow=100)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# [ADMIN] reply button Админ
async def admin(message: types.Message):
    try:
        user_admin = [952604184, 5742872990]
        list_users = types.InlineKeyboardButton(text='Список пользователей', callback_data='list_users')
        list_wallets = types.InlineKeyboardButton(text='Список кошельков', callback_data='list_wallets')
        button_exit = types.InlineKeyboardButton(text='Выйти из админки', callback_data='mywallets')
        text = f'[Вы находитесь в панели администратора]\n' \
               f'\n'\
               f'Здесь должны быть:\n'\
               f'[   ] Списки всех пользователей обменника\n'\
               f'[   ] Список кошельков, зарегистрированных в обменнике\n'\
               f'[   ] Отчетность по операциям на кошельках\n'\
               f'[   ] Балансы адресов\n'\
               f'[   ] Запросы на перевод'
        reply_markup = types.InlineKeyboardMarkup(row_width=1).add(list_users, list_wallets, button_exit)
        if message.from_user.id in user_admin:
            await bot.send_message(chat_id=message.from_user.id,
                                   text=text,
                                   reply_markup=reply_markup)
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text='У вас недостаточно прав для просмотра этой категории.')

    except Exception as e:
        logging.error(f' [ADMIN] reply button {message.from_user.id} - Ошибка в функции admin: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[ADMIN] reply button {message.from_user.id} - '
                                    f'Произошла ошибка в функции admin: {e}')


# [ADMIN] inline button Админ
async def admin_callback(callback_query: types.CallbackQuery):
    try:
        user_admin = [952604184, 5742872990]
        list_users = types.InlineKeyboardButton(text='Список пользователей', callback_data='list_users')
        list_wallets = types.InlineKeyboardButton(text='Список кошельков', callback_data='list_wallets')
        button_exit = types.InlineKeyboardButton(text='Выйти из админки', callback_data='mywallets')

        text = f'[Вы находитесь в панели администратора]\n' \
               f'\n'\
               f'Здесь должны быть:\n'\
               f'[   ] Списки всех пользователей обменника\n'\
               f'[   ] Список кошельков, зарегистрированных в обменнике\n'\
               f'[   ] Отчетность по операциям на кошельках\n'\
               f'[   ] Балансы адресов\n'\
               f'[   ] Запросы на перевод'

        reply_markup = types.InlineKeyboardMarkup(row_width=1).add(list_users, list_wallets, button_exit)

        if callback_query.from_user.id in user_admin:
            await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=reply_markup)

    except Exception as e:
        logging.error(f' [ADMIN] inline button {callback_query.from_user.id} - Ошибка в функции admin: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[ADMIN] inline button {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции admin: {e}')
