from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, DB_URL
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from datetime import datetime
import logging


logging.basicConfig(filename='bot.log', level=logging.INFO)

engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# [START]
async def start(message: types.Message):
    try:
        wallet_button = types.KeyboardButton('Кошелек')
        one_button = types.KeyboardButton('One')
        two_button = types.KeyboardButton('Two')
        three_button = types.KeyboardButton('Three')
        start_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).\
            add(wallet_button, one_button, two_button, three_button)

        start_text = f'Привет, это тестовый бот\n'

        await bot.send_message(chat_id=message.from_user.id,
                               text=start_text,
                               reply_markup=start_keyboard)

        session = Session()
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        session.close()

        if user:
            if user.telegram_id == 952604184 or user.telegram_id == 5742872990:
                wallet_button = types.KeyboardButton('Кошелек')
                one_button = types.KeyboardButton('One')
                two_button = types.KeyboardButton('Two')
                three_button = types.KeyboardButton('Three')
                admin_button = types.KeyboardButton('Админ')
                start_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True). \
                    add(wallet_button, one_button, two_button, three_button).row(admin_button)

                start_text = f'Вы - администратор. Зайти в панель администратора можно по кнопке - Админ\n' \
                             f'\n' \
                             f'Здесь должны быть:\n' \
                             f'[   ] Списки всех пользователей обменника\n' \
                             f'[   ] Список кошельков, зарегистрированных в обменнике\n' \
                             f'[   ] Отчетность по операциям на кошельках\n' \
                             f'[   ] Балансы адресов\n' \
                             f'[   ] Запросы на перевод'

                await bot.send_message(chat_id=message.from_user.id,
                                       text=start_text,
                                       reply_markup=start_keyboard)

            else:

                menu_buttons = types.InlineKeyboardMarkup(row_width=2)
                register_button = types.InlineKeyboardButton(text='Регистрация кошелька', callback_data='register')
                my_wallets_button = types.InlineKeyboardButton(text='Мои кошельки', callback_data='mywallets')
                menu_buttons.add(register_button, my_wallets_button)

                comeback_text = f'Добро пожаловать!\n' \
                                f'\n' \
                                f'Ваш аккаунт:\n' \
                                f'ID аккаунта: {user.telegram_id}\n' \
                                f'Дата создания: {user.reg_date}'

                await bot.send_message(chat_id=message.from_user.id,
                                       text=comeback_text,
                                       reply_markup=menu_buttons)
        else:
            register_button = types.InlineKeyboardButton(text='Регистрация кошелька', callback_data='register')
            menu_register = types.InlineKeyboardMarkup()
            menu_register.add(register_button)

            session = Session()
            new_user = User(telegram_id=message.from_user.id, username=message.from_user.username)
            session.add(new_user)
            session.commit()
            session.close()

            welcome_text = f'Добро пожаловать!\n' \
                           f'\n' \
                           f'Ваш аккаунт успешно создан.\n' \
                           f'ID аккаунта: {message.from_user.id}\n' \
                           f'Дата создания: {datetime.today().strftime("%Y-%m-%d %H:%M")}'

            await bot.send_message(chat_id=message.from_user.id,
                                   text=welcome_text,
                                   reply_markup=menu_register)

    except Exception as e:
        logging.error(f'{message.from_user.id} - ошибка в функции start: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'[START] {message.from_user.id} - Произошла ошибка в функции start: {e}')
