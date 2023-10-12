from aiogram import Bot, Dispatcher, executor, types, filters
from config import DB_URL, TOKEN
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
import asyncio


engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# [LIST USERS] callback_data='list_users'
async def list_users(callback_query: types.CallbackQuery):
    try:
        session = Session()
        users = session.query(User).all()
        session.close()

        buttons = []
        users_count = 0

        for user in users:
            users_count += 1
            button_text = f'«{user.telegram_id}» - {user.username}, дата регистрации: {user.reg_date}'
            buttons.append(types.InlineKeyboardButton(text=button_text, callback_data=f'click_user_{user.telegram_id}'))

        text = f'[Вы находитесь в панели администратора]\n' \
               f'\n'\
               f'Всего зарегистрировано {users_count} пользователей.\n'\
               f'[ 🐰 ] Список всех пользователей обменника:\n'\

        button_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data='admin')
        reply_markup = types.InlineKeyboardMarkup(row_width=1).add(*buttons, button_back)

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

    except Exception as e:
        await bot.send_message(chat_id='952604184',
                               text=f'[LIST USERS] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции list_users: {e}')
