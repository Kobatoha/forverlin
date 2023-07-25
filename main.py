from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, TELEGRAM_ID, DB_URL
from parser import parser_main
import json
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Transactions, User
from datetime import datetime
from aiocron import crontab
import asyncio


engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['register'])
async def start_register(message: types.Message):
    await message.answer('Hello, insert your wallet id')
    session = Session()
    user = User(telegram_id=message.from_user.id)
    session.add(user)
    session.commit()
    session.close()


@dp.message_handler(lambda message: message.text.isalnum() and len(message.text) >= 30)
async def save_wallet_id(message: types.Message):
    session = Session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if user:
        user.wallet = message.text
        session.commit()
        await message.answer('Your wallet id is saved')
        session.close()
    else:
        await message.answer('You need to register first. Use /register command')
        session.close()


@dp.message_handler(lambda message: message.text == '/start')
async def start_again(message: types.Message):
    session = Session()
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if user:
        await message.answer('Welcome back!')
    else:
        await message.answer('Use /register command to create an account')
    session.close()


@dp.message_handler(lambda message: not (message.text.isalnum() and len(message.text) >= 30))
async def wrong_input(message: types.Message):
    await message.answer('Wrong input. Please insert your wallet correct id')


async def send_transaction_info():
    session = Session()

    users = session.query(User).all()
    for user in users:
        print(f"Telegram ID: {user.telegram_id}")
        print(f"Wallet address: {user.wallet}")
        transactions = session.query(Transactions).filter(
            Transactions.to_address == user.wallet,
            Transactions.token_abbr == 'USDT',
            Transactions.send_message == False,
        ).all()

        for transaction in transactions:
            count = transaction.count
            if len(count) > 6:
                print(transaction.count)
                if count[-6:] == '000000':
                    count = count[:-9] + ',' + count[-9:-6]
                else:
                    count = count[:-9] + ',' + count[-9:-6] + '.' + count[-6:]

                message_text = f"+{count} USDT"
                await bot.send_message(chat_id=user.telegram_id, text=message_text)

                transaction.send_message = True
            session.commit()

    session.close()


async def crontab_parser():
    # Запускаем парсер каждую минуту
    crontab('*/1 * * * *', func=parser_main)

    # Запускаем функцию send_transaction_info каждую минуту
    crontab('*/1 * * * *', func=send_transaction_info)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(crontab_parser())
    executor.start_polling(dp, skip_updates=True)
