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

proxy_login = 'J682y3'
proxy_pass = '76jbez'

proxies = [
    '217.29.63.202:12615',
    '217.29.63.202:12532',
    '217.29.63.202:12531',
    '217.29.63.202:12530',
    '217.29.63.202:12529',
    '217.29.63.40:10587'
]

address = 'https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=3&start=0&sort=-timestamp&count=true&filterTokenValue=0&relatedAddress=TXxTs2x6YXoiZXLLJZXmGFvyYCgTJiPzuh'


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
        for proxy in proxies:
            print(proxy)
            async with session.get(address) as response:
                print(response.status)

                if response.status == 200:
                    parsed_data = await response.json()
                    token_transfers = parsed_data['token_transfers']
                    for transfer in token_transfers:
                        dict_ = {
                                    'quant': transfer['quant'],
                                    'from_address': transfer['from_address'],
                                    'to_address': transfer['to_address'],
                                    'transaction_id': transfer['transaction_id'],
                                    'tokenAbbr': transfer['tokenInfo']['tokenAbbr']
                                }
                        print(dict_)
                else:
                    print(f"Ошибка при получении данных. Статус: {response.status}")


async def parser_main():
    await get_data("https://tronscan.org/#/address/TXxTs2x6YXoiZXLLJZXmGFvyYCgTJiPzuh/transfers")


if __name__ == '__main__':
    asyncio.run(parser_main())
