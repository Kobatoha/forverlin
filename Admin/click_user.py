from aiogram import Bot, Dispatcher, executor, types, filters
from config import DB_URL, TOKEN
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from DataBase.WalletTron import WalletTron
import asyncio


engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# [CLICK USER] lambda c: c.data.startswith('click_user_')
async def click_user(callback_query: types.CallbackQuery):
    try:
        user_id = callback_query.data.split('_')[2]
        session = Session()
        user = session.query(User).filter_by(telegram_id=user_id).first()
        wallets_address = session.query(WalletTron).filter_by(telegram_id=user_id).all()
        session.close()

        buttons = []
        wallets_address_count = 0
        wallets_address_only_watch = 0

        for wallet in wallets_address:
            wallets_address_count += 1
            if wallet.only_watch:
                wallets_address_only_watch += 1
            else:
                button_text = f'«{wallet.wallet_name}» - {wallet.wallet_address[:3]}...{wallet.wallet_address[-3:]}'
                buttons.append(types.InlineKeyboardButton(
                    text=button_text,
                    callback_data=f'click_user_{user_id}_{wallet.wallet_address}'))

        text = f'[Пользователь «{user_id}» - {user.username}]\n' \
               f'\n'\
               f'[ 🐰 ] Регистрация: {user.reg_date}\n' \
               f'[ 🐰 ] Всего кошельков: {wallets_address_count}\n' \
               f'[ 🐰 ] Кошельки для чтения: {wallets_address_only_watch}\n'\
               f'[ 🐰 ] Запросов на обмен: 0\n' \
               f'[ 🐰 ] Запросов на вывод: 0\n' \
               f'[ 🐰 ] Еще что-нибудь: 0'\

        button_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data='list_users')
        reply_markup = types.InlineKeyboardMarkup(row_width=1).add(*buttons, button_back)

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

    except Exception as e:
        await bot.send_message(chat_id='952604184',
                               text=f'[CLICK USERS] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции click_user: {e}')
