import time
import requests
import aiohttp
import asyncio
import gzip
from io import BytesIO
from bs4 import BeautifulSoup
import json
from config import DB_URL
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.Base import Base
from DataBase.User import User
from DataBase.TrustedUser import TrustedUser
from DataBase.WalletTron import WalletTron
from DataBase.Transaction import Transaction
from datetime import datetime


engine = create_engine(DB_URL, pool_size=50, max_overflow=40)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


async def get_data(url):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/114.0.0.0 Safari/537.36'
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        session_db = Session()
        users = session_db.query(WalletTron).all()
        session_db.close()
        for user in users:
            if user.wallet_address is not None:
                wallet_address = user.wallet_address

                async with session.get(
                        f"https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=3&start=0&sort="
                        f"-timestamp&count=true&filterTokenValue=0&relatedAddress={wallet_address}") as response:
                    if response.status == 200:

                        parsed_data = await response.json()

                        token_transfers = parsed_data['token_transfers']

                        for transfer in token_transfers:
                            now = datetime.now().strftime('%H:%M')
                            day = datetime.today()
                            sub_session = Session()
                            dict_ = {
                                'quant': transfer['quant'],
                                'from_address': transfer['from_address'],
                                'to_address': transfer['to_address'],
                                'transaction_id': transfer['transaction_id'],
                                'tokenAbbr': transfer['tokenInfo']['tokenAbbr']
                            }

                            if not sub_session.query(Transaction).filter_by(
                                    transaction_id=dict_['transaction_id']).first():

                                trans = Transaction(
                                    wallet_address=wallet_address,
                                    transaction_id=dict_['transaction_id'],
                                    token_abbr=dict_['tokenAbbr'],
                                    count=dict_['quant'],
                                    from_address=dict_['from_address'],
                                    to_address=dict_['to_address'],
                                    date=day,
                                    time=now,
                                )

                                sub_session.add(trans)
                                print(trans.wallet_address, trans.transaction_id, trans.token_abbr, trans.count,
                                      trans.from_address, trans.to_address, trans.date, trans.time)
                                sub_session.commit()
                                print(now, 'Добавляется новая транзакция в', user.wallet_name)
                            sub_session.close()
                    else:
                        print(f"Ошибка при получении данных. Статус: {response.status}")
                        await asyncio.sleep(120)
                        return {}

                    await asyncio.sleep(5)  # добавляем задержку между запросами

        session_db.close()


async def parser_main():
    tasks = []
    session = Session()
    wallets = session.query(WalletTron).all()
    for wallet in wallets:
        wallet_address = wallet.wallet_address
        task = asyncio.create_task(get_data(f"https://tronscan.org/#/address/{wallet_address}/transfers"))
        tasks.append(task)
    await asyncio.gather(*tasks)
    session.close()


if __name__ == '__main__':
    asyncio.run(parser_main())
