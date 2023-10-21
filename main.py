from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN, DB_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from DataBase.TrustedUser import TrustedUser
from DataBase.WalletTron import WalletTron
from DataBase.Transaction import Transaction
from datetime import datetime
from command_imports import *
import asyncio
from aiocron import crontab

engine = create_engine(DB_URL, pool_size=100, max_overflow=100)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dp.register_message_handler(start, commands=['start'])                                          # [START]
dp.register_callback_query_handler(register_wallet, text_contains='register')                   # [REGISTER WALLET]
dp.register_callback_query_handler(
    add_wallet_address,
    lambda callback_query: callback_query.data == 'add_wallet_address')                         # [ADD WALLET ADDRESS]
dp.register_callback_query_handler(
    cancel_add_wallet_address,
    lambda callback_query: callback_query.data == 'cancel_add_wallet_address',
    state=WalletRegistration.waiting_for_wallet_id)                                        # [CANCEL ADD WALLET ADDRESS]
dp.register_message_handler(save_wallet_address,
                            state=WalletRegistration.waiting_for_wallet_id)                     # [SAVE WALLET ADDRESS]
dp.register_message_handler(wallets, text_contains='Кошелек')                                   # [WALLETS] reply
dp.register_callback_query_handler(my_wallets, text_contains='mywallets')                       # [MY WALLETS] inline
dp.register_callback_query_handler(confirm_create_tron_wallet,
                                   text_contains='confirm_create_tron_wallet')            # [CONFIRM CREATE TRON WALLET]
dp.register_callback_query_handler(create_tron_wallet, text_contains='create_tron_wallet')      # [CREATE TRON WALLET]
dp.register_callback_query_handler(
    back_to_registration,
    lambda callback_query: callback_query.data == 'back_to_registration')                       # [BACK TO REGISTRATION]
dp.register_callback_query_handler(click_wallet, lambda c: c.data.startswith('wallet_'))        # [CLICK WALLET]
dp.register_callback_query_handler(edit_wallet_name, lambda c: c.data.startswith('edit_'))      # [EDIT WALLET NAME]
dp.register_callback_query_handler(
    cancel_edit_wallet_name,
    lambda c: c.data.startswith('cancel_edit_wallet_name_'),
    state=WalletNameEdit.waiting_for_new_name)                                               # [CANCEL EDIT WALLET NAME]
dp.register_callback_query_handler(get_wallet_address,
                                   lambda c: c.data.startswith('get_address_'))                 # [GET WALLET ADDRESS]
dp.register_message_handler(save_wallet_name, state=WalletNameEdit.waiting_for_new_name)        # [SAVE WALLET NAME]
dp.register_callback_query_handler(delete_wallet, lambda c: c.data.startswith('delete_'))       # [DELETE WALLET]
dp.register_callback_query_handler(confirm_delete_wallet,
                                   text_contains='confirm_delete_')                            # [CONFIRM DELETE WALLET]
dp.register_callback_query_handler(share_wallet, lambda c: c.data.startswith('share_'))         # [SHARE WALLET]
dp.register_callback_query_handler(
    cancel_share_wallet,
    lambda c: c.data.startswith('cancel_share_wallet_'),
    state=ShareWallet.waiting_for_trusted_username)                                             # [CANCEL SHARE WALLET]
dp.register_message_handler(save_trusted_user, state=ShareWallet.waiting_for_trusted_username)  # [SAVE TRUSTED USER]
dp.register_callback_query_handler(trusted_users,
                                   lambda c: c.data.startswith('trusted_users_'))               # [TRUSTED USERS]
dp.register_callback_query_handler(choice_remove_trusted_user,
                                   lambda c: c.data.startswith('trusted_user_remove_'))   # [CHOICE REMOVE TRUSTED USER]
dp.register_callback_query_handler(remove_user,
                                   lambda c: c.data.startswith('remove_'))                      # [DELETE TRUSTED USER]
dp.register_message_handler(admin, text_contains='Админ')                                       # [ADMIN] reply
dp.register_callback_query_handler(admin_callback, text_contains='admin')                       # [ADMIN] inline
dp.register_callback_query_handler(list_users, text_contains='list_users')                      # [LIST USERS]
dp.register_callback_query_handler(click_user, lambda c: c.data.startswith('click_user_'))      # [CLICK USER]
dp.register_callback_query_handler(click_user_wallet,
                                   lambda c: c.data.startswith('click_wallet_user_'))           # [CLICK USER WALLET]
dp.register_callback_query_handler(list_wallets, text_contains='list_wallets')                  # [LIST WALLETS]


# [SEND TRANSACTION]
async def send_transaction_info():
    try:
        print('Start trans')
        today = datetime.today().date()
        print(today)
        session = Session()

        wallets = session.query(WalletTron).all()
        for wallet in wallets:
            transactions = session.query(Transaction).filter(Transaction.to_address == wallet.wallet_address,
                                                             Transaction.token_abbr == 'USDT',
                                                             Transaction.send_message.is_(False),
                                                             Transaction.date == today).all()

            for transaction in transactions:
                count = transaction.count
                print(transaction.wallet_address, '->', transaction.token_abbr, count)
                message_text = None
                if len(count) > 9:
                    print(f'[SEND TRANSACTION] {wallet.wallet_name} - add {transaction.count}')
                    if count[-6:] == '000000':
                        count = count[:-9] + ',' + count[-9:-6]
                    else:
                        count = count[:-9] + ',' + count[-9:-6] + '.' + count[-6:]
                    message_text = f"{wallet.wallet_name}: +{count} USDT"

                elif len(count) == 9:
                    print(f'[SEND TRANSACTION] {wallet.wallet_name} - add {transaction.count}')
                    count = count[:3]
                    message_text = f"{wallet.wallet_name}: +{count} USDT"

                elif len(count) == 8:
                    print(f'[SEND TRANSACTION] {wallet.wallet_name} - add {transaction.count}')
                    count = count[:2]
                    message_text = f"{wallet.wallet_name}: +{count} USDT"

                elif len(count) == 7:
                    print(f'[SEND TRANSACTION] {wallet.wallet_name} - add {transaction.count}')
                    count = count[:1]
                    message_text = f"{wallet.wallet_name}: +{count} USDT"

                print(message_text)

                if message_text:
                    trust_users = session.query(TrustedUser).filter_by(wallet_address=wallet.wallet_address).all()

                    for trusted_user in trust_users:
                        in_all_user = session.query(User).filter_by(username=trusted_user.username[1:]).first()
                        if in_all_user and in_all_user.username == trusted_user.username[1:]:
                            print(f"trusted_user - {trusted_user.username} have a message from "
                                  f"{trusted_user.wallet_address}")
                            chat_id = in_all_user.telegram_id
                            await bot.send_message(chat_id=chat_id, text=message_text)

                    await bot.send_message(chat_id=wallet.telegram_id, text=message_text)
                    transaction.send_message = True
                    session.commit()
        session.close()

    except Exception as error:
        await bot.send_message(chat_id='952604184',
                               text=f'Произошла ошибка в функции send_transaction_info: {error}')


async def crontab_parser():
    # Запускаем парсер каждую минуту
    crontab('*/1 * * * *', func=parser_main)
    print('Запустили парсер')

    # Запускаем функцию send_transaction_info каждую минуту
    crontab('*/1 * * * *', func=send_transaction_info)
    print('Запустили send_transaction')


async def send_error():
    now_error = datetime.now().strftime('%H:%M:%S')
    await bot.send_message(chat_id='952604184',
                           text=f'{now_error}: Произошла ошибка в работе телеграм бота: {e}')


if __name__ == '__main__':
    try:
        now_start = datetime.now().strftime('%H:%M:%S')
        loop = asyncio.get_event_loop()
        loop.create_task(crontab_parser())
        print(f'{now_start}: start "Стратый грузин" bot')
        executor.start_polling(dp, skip_updates=True)

    except Exception as e:
        now = datetime.now().strftime('%H:%M:%S')
        print(f'{now}: Произошла ошибка в работе телеграм бота, {e}')
