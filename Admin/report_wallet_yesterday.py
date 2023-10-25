from aiogram import Bot, Dispatcher, executor, types, filters
from config import DB_URL, TOKEN
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from DataBase.WalletTron import WalletTron
import asyncio
import datetime
from test_func.get_trongrid_transactions_yesterday import get_trongrid_transactions_yesterday


engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# [REPORT WALLET YESTERDAY]
async def report_wallet_yesterday(callback_query: types.CallbackQuery):
    try:
        wallet_address = callback_query.data.split('_')[2]

        text = await get_trongrid_transactions_yesterday(wallet_address)
        print(text)

        button_back = types.InlineKeyboardButton(
            text='Вернуться назад',
            callback_data=f'click_wallet_user_{wallet_address}')

        reply_markup = types.InlineKeyboardMarkup(row_width=1).add(button_back)

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

    except Exception as e:
        await bot.send_message(chat_id='952604184',
                               text=f'[REPORT WALLET YESTERDAY] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции report_wallet_yesterday: {e}')
