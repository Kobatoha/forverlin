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


# [LIST WALLETS]  callback_data='list_wallets')
async def list_wallets(callback_query: types.CallbackQuery):
    try:
        session = Session()
        wallets = session.query(WalletTron).all()
        session.close()

        wallets_count = 0

        for wallet in wallets:
            if wallet:
                wallets_count += 1

        text = f'[Вы находитесь в панели администратора]\n' \
               f'\n'\
               f'[ 🦊 ] Всего кошельков: {wallets_count}\n'\
               f'[ 🦊 ] Общий баланс: 0.00\n'\

        button_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data='admin')
        reply_markup = types.InlineKeyboardMarkup(row_width=1).add(button_back)

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

    except Exception as e:
        await bot.send_message(chat_id='952604184',
                               text=f'[LIST WALLETS] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции list_wallets: {e}')
