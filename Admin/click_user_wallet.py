from aiogram import Bot, Dispatcher, executor, types, filters
from config import DB_URL, TOKEN
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from DataBase.WalletTron import WalletTron
import asyncio
from Functions.balance import get_balance_usdt


engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# [CLICK USER WALLET]
async def click_user_wallet(callback_query: types.CallbackQuery):
    try:
        wallet_address = callback_query.data.split('_')[3]
        session = Session()
        wallet = session.query(WalletTron).filter_by(wallet_address=wallet_address).first()
        user = session.query(User).filter_by(telegram_id=wallet.telegram_id).first()
        session.close()

        balance_ = await get_balance_usdt(wallet_address)
        if not balance_:
            balance_ = 0.00

        text = f'[Пользователь «{user.telegram_id}» - {user.username} - кошелек «{wallet_address}»]\n' \
               f'\n'\
               f'[ 🐰 ] Протокол: trc20\n' \
               f'[ 🐰 ] Баланс: {balance_}\n' \
               f'[ 🐰 ] Только для чтения: {wallet.only_watch}\n'\
               f'[ 🐰 ] Запросов на обмен: 0\n' \
               f'[ 🐰 ] Запросов на вывод: 0\n' \
               f'[ 🐰 ] Еще что-нибудь: 0'\

        button_back = types.InlineKeyboardButton(text='Вернуться назад', callback_data=f'click_user_{user.telegram_id}')
        reply_markup = types.InlineKeyboardMarkup(row_width=1).add(button_back)

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)

    except Exception as e:
        await bot.send_message(chat_id='952604184',
                               text=f'[CLICK USER WALLET] {callback_query.from_user.id} - '
                                    f'Произошла ошибка в функции click_user_wallet: {e}')
