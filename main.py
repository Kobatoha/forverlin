from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, DB_URL
from parser import parser_main
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from DataBase.TrustedUser import TrustedUser
from DataBase.WalletTron import WalletTron
from DataBase.WatchWallet import WatchWallet
from DataBase.TransactionWatchWallet import TransactionWatchWallet
from datetime import datetime
from aiocron import crontab
import asyncio
import logging
from Commands.command_imports import *

logging.basicConfig(filename='bot.log', level=logging.INFO)

engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dp.register_callback_query_handler(create_tron_wallet, text_contains='create_tron_wallet')      # [CREATE TRON WALLET]
dp.register_message_handler(save_wallet_id, state=WalletRegistration.waiting_for_wallet_id)     # [SAVE WALLET ID]
dp.register_callback_query_handler(start_register, text_contains='register')                    # [START REGISTER]
dp.register_callback_query_handler(
    cancel_to_register,
    lambda callback_query: callback_query.data == 'cancel_to_register',
    state=WalletRegistration.waiting_for_wallet_id)                                             # [CANCEL TO REGISTER]
dp.register_message_handler(start, commands=['start'])                                          # [START]
dp.register_message_handler(wallets, text_contains='Кошелек')                                   # [WALLETS] reply
dp.register_callback_query_handler(
    insert_wallet_id,
    lambda callback_query: callback_query.data == 'insert_wallet_id')                           # [INSERT WALLET ID]
dp.register_callback_query_handler(my_wallets, text_contains='mywallets')                       # [MY WALLETS] inline
dp.register_callback_query_handler(
    back_to_registration,
    lambda callback_query: callback_query.data == 'back_to_registration')                       # [BACK TO REGISTRATION]
dp.register_callback_query_handler(click_wallet, lambda c: c.data.startswith('wallet_'))        # [CLICK WALLET]
dp.register_callback_query_handler(edit_wallet_name, lambda c: c.data.startswith('edit_'))      # [EDIT WALLET NAME]
dp.register_callback_query_handler(
    cancel_to_edit_wallet_name,
    lambda c: c.data.startswith('cancel_to_edit_wallet_name_'),
    state=WalletNameEdit.waiting_for_new_name)                                       # [CANCEL FOR CHANGE WALLET NAME]
dp.register_callback_query_handler(get_wallet_address,
                                   lambda c: c.data.startswith('get_address_'))                 # [GET WALLET ADDRESS]
dp.register_message_handler(save_wallet_name, state=WalletNameEdit.waiting_for_new_name)        # [SAVE WALLET NAME]
dp.register_callback_query_handler(delete_wallet, lambda c: c.data.startswith('delete_'))       # [DELETE WALLET]
dp.register_callback_query_handler(share_wallet, lambda c: c.data.startswith('share_'))         # [SHARE WALLET]
dp.register_callback_query_handler(
    cancel_to_share_wallet,
    lambda c: c.data.startswith('cancel_to_share_wallet_'),
    state=ShareWallet.waiting_for_trusted_username)                                             # [CANCEL SHARE WALLET]
dp.register_message_handler(save_trusted_user, state=ShareWallet.waiting_for_trusted_username)  # [SAVE TRUSTED USER]


menu_buttons = types.InlineKeyboardMarkup(row_width=2)
register_button = types.InlineKeyboardButton(text='Register', callback_data='register')
my_wallets_button = types.InlineKeyboardButton(text='My Wallets', callback_data='mywallets')
menu_buttons.add(register_button, my_wallets_button)

menu_register = types.InlineKeyboardMarkup()
menu_register.add(register_button)


class WalletNameEdit(StatesGroup):
    waiting_for_new_name = State()


class ShareWallet(StatesGroup):
    waiting_for_trusted_username = State()


inline_register_buttons = types.InlineKeyboardMarkup()

button_yes = types.InlineKeyboardButton(text='insert wallet id', callback_data='insert_wallet_id')
button_no = types.InlineKeyboardButton(text='<< back', callback_data='back_to_reg')

inline_register_buttons.add(button_yes, button_no)


### BACK TO MENU
@dp.callback_query_handler(lambda c: c.data == 'back')
async def back_callback(callback_query: types.CallbackQuery):
    try:
        now = datetime.now().strftime('%H:%M:%S')
        logging.info(f'[BACK TO MENU] {now}: {callback_query.from_user.id} - {callback_query.from_user.username} '
                     f'возврат в меню кошельков')
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Ваши кошельки:')
        await my_wallets(callback_query.message)

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции back_callback: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{callback_query.from_user.id} - Произошла ошибка в функции back_callback:'
                                    f' {e}')


### CLICK TRUSTED USERS FOR WALLET
@dp.callback_query_handler(lambda c: c.data.startswith('trusted_users_'))
async def trusted_users(callback_query: types.CallbackQuery):
    try:
        now = datetime.now().strftime('%H:%M:%S')
        logging.info(f'[CLICK TRUSTED USERS FOR WALLET] {now}: {callback_query.from_user.id} - '
                     f'{callback_query.from_user.username} список доверенных пользователей')

        # получение кошелька из callback_data
        wallet = callback_query.data.split('_')[2]

        # получение списка доверенных пользователей для данного кошелька
        session = Session()
        trusted_users = session.query(TrustedUser).filter_by(wallet=wallet).all()
        session.close()

        if not trusted_users:
            text = 'Нет доверенных пользователей для этого кошелька'
        else:
            text = 'Доверенные пользователи для этого кошелька:\n'
            for user in trusted_users:
                text += f'- {user.username}\n'

        buttons = [
            types.InlineKeyboardButton(text='Добавить пользователя', callback_data=f'share_{wallet}'),
            types.InlineKeyboardButton(text='Удалить пользователя', callback_data=f'turemove_{wallet}'),
            types.InlineKeyboardButton(text='<< back', callback_data=f'wallet_{wallet}')
        ]
        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(*buttons)

        await bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id,
                                    text=text, reply_markup=reply_markup)

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции trusted_users: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{callback_query.from_user.id} - Произошла ошибка в функции '
                                    f'trusted_users: {e}')


### CHOICE REMOVE TRUSTED USER
@dp.callback_query_handler(lambda c: c.data.startswith('turemove'))
async def process_remove_user(callback_query: types.CallbackQuery):
    try:
        now = datetime.now().strftime('%H:%M:%S')
        logging.info(f'[CHOICE REMOVE TRUSTED USER] {now}: {callback_query.from_user.id} - '
                     f'{callback_query.from_user.username} процесс удаления доверенного пользователя')

        # получение данных из callback_data
        data = callback_query.data.split('_')
        wallet = data[1]

        # редактирование исходного сообщения
        text = f'Какого пользователя вы желаете отключить от уведомлений {wallet}?'
        reply_markup = types.InlineKeyboardMarkup(row_width=1)

        # получение списка доверенных пользователей для данного кошелька
        session = Session()
        trusted_users = session.query(TrustedUser).filter_by(wallet=wallet).all()
        session.close()

        # создание кнопок для каждого доверенного пользователя
        buttons = []
        for trusted_user in trusted_users:
            buttons.append(types.InlineKeyboardButton(text=f'Удалить {trusted_user.username}',
                                                      callback_data=f'uremove_{wallet}_{trusted_user.username}'))

        # добавление кнопок в клавиатуру
        buttons.append(types.InlineKeyboardButton(text='<< back', callback_data=f'trusted_users_{wallet}'))
        reply_markup.add(*buttons)

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)
    except MessageNotModified:
        pass
    except MessageToDeleteNotFound:
        await bot.send_message(chat_id=callback_query.from_user.id, text=text, reply_markup=reply_markup)
    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции process_remove_user: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{callback_query.from_user.id} - Произошла ошибка в функции '
                                    f'process_remove_user: {e}')


# DELETE TRUSTED USER
@dp.callback_query_handler(lambda c: c.data.startswith('uremove'))
async def remove_user(callback_query: types.CallbackQuery):
    try:
        now = datetime.now().strftime('%H:%M:%S')
        logging.info(f'[DELETE TRUSTED USER] {now}: {callback_query.from_user.id} - {callback_query.from_user.username}'
                     f' удаление доверенного пользователя')
        # получение данных из callback_data
        data = callback_query.data.split('_')
        wallet = data[1]
        username = data[2]

        # удаление пользователя из базы данных
        session = Session()
        user = session.query(User).filter_by(wallet=wallet).first()
        trusted_user = session.query(TrustedUser).filter_by(username=username, wallet=user.wallet).first()
        session.delete(trusted_user)
        session.commit()
        logging.info(f'[DELETE TRUSTED USER] {now}: {callback_query.from_user.id} - {callback_query.from_user.username}'
                     f' доверенный пользователь удален')
        session.close()

        back_button = types.InlineKeyboardButton(text='<< back', callback_data='mywallets')
        reply_markup = types.InlineKeyboardMarkup(row_width=1)
        reply_markup.add(back_button)

        text = f'Пользователь {trusted_user.username} удален из списка пользователей, ' \
               f'следящих за транзакциями в кошельке {trusted_user.wallet}'

        await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=reply_markup)
    except MessageNotModified:
        pass
    except MessageToDeleteNotFound:
        await bot.send_message(chat_id=callback_query.from_user.id, text=text, reply_markup=reply_markup)

        await bot.answer_callback_query(callback_query_id=callback_query.id)

    except Exception as e:
        logging.error(f'{callback_query.from_user.id} - Ошибка в функции remove_user: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'{callback_query.from_user.id} - Произошла ошибка в функции '
                                    f'remove_user: {e}')


# SEND TRANSACTION
async def send_transaction_info():
    try:
        now = datetime.now().strftime('%H:%M:%S')
        session = Session()

        users = session.query(WatchWallet).all()
        for user in users:
            logging.info(f"[SEND TRANSACTION] {now}: Telegram ID: {user.telegram_id} - "
                         f"{user.username}, with {user.wallet_name} - {user.wallet_address}")

            transactions = session.query(TransactionWatchWallet).filter(
                TransactionWatchWallet.wallet_address == user.wallet_address,
                TransactionWatchWallet.to_address == user.wallet_address,
                TransactionWatchWallet.token_abbr == 'USDT',
                TransactionWatchWallet.send_message == False
            ).all()

            for transaction in transactions:
                count = transaction.count
                message_text = None
                if len(count) > 9:
                    logging.info(f'[SEND TRANSACTION] {user.wallet_name} - add {transaction.count}')
                    if count[-6:] == '000000':
                        count = count[:-9] + ',' + count[-9:-6]
                    else:
                        count = count[:-9] + ',' + count[-9:-6] + '.' + count[-6:]
                    message_text = f"{user.wallet_name}: +{count} USDT"

                elif len(count) == 9:
                    logging.info(f'[SEND TRANSACTION] {user.wallet_name} - add {transaction.count}')
                    count = count[:3]
                    message_text = f"{user.wallet_name}: +{count} USDT"

                elif len(count) == 8:
                    logging.info(f'[SEND TRANSACTION] {user.wallet_name} - add {transaction.count}')
                    count = count[:2]
                    message_text = f"{user.wallet_name}: +{count} USDT"

                elif len(count) == 7:
                    logging.info(f'[SEND TRANSACTION] {user.wallet_name} - add {transaction.count}')
                    count = count[:1]
                    message_text = f"{user.wallet_name}: +{count} USDT"

                if message_text:
                    trusted_users = session.query(TrustedUser).filter_by(wallet_address=user.wallet_address).all()

                    for trusted_user in trusted_users:
                        in_all_user = session.query(User).filter_by(username=trusted_user.username[1:]).first()
                        if in_all_user and in_all_user.username == trusted_user.username[1:]:
                            print(f"trusted_user - {trusted_user.username} have a message from "
                                  f"{trusted_user.wallet_address}")
                            chat_id = in_all_user.telegram_id
                            await bot.send_message(chat_id=chat_id, text=message_text)

                    await bot.send_message(chat_id=user.telegram_id, text=message_text)
                    logging.info(f'[SEND TRANSACTION] Пользователь {user.telegram_id} - {user.username} '
                                 f'получил сообщение о транзакции: {message_text}')
                    transaction.send_message = True
                    session.commit()
        session.close()

    except Exception as e:
        logging.error(f'Ошибка в функции send_transaction_info: {e}')
        await bot.send_message(chat_id='952604184',
                               text=f'Произошла ошибка в функции send_transaction_info: {e}')


async def crontab_parser():

    # Запускаем парсер каждую минуту
    crontab('*/1 * * * *', func=parser_main)

    # Запускаем функцию send_transaction_info каждую минуту
    crontab('*/1 * * * *', func=send_transaction_info)


async def send_error():
    now = datetime.now().strftime('%H:%M:%S')
    await bot.send_message(chat_id='952604184',
                           text=f'{now}: Произошла ошибка в работе телеграм бота: {e}')


if __name__ == '__main__':
    try:
        now = datetime.now().strftime('%H:%M:%S')
        #loop = asyncio.get_event_loop()
        #loop.create_task(crontab_parser())
        print(f'{now}: start "Стратый грузин" bot')
        executor.start_polling(dp, skip_updates=True)

    except Exception as e:
        now = datetime.now().strftime('%H:%M:%S')
        logging.error(f'{now}: Ошибка в работе телеграм бота: {e}')
        send_error()
