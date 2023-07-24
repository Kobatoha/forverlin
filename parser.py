import requests
import gzip
from io import BytesIO
from bs4 import BeautifulSoup
import json
from config import WALLET, TELEGRAM_ID, DB_URL
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Transactions, User
from datetime import datetime


engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)


def get_data(url):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    r = requests.get("https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=50&start=0&sort=-timestamp&count=true&filterTokenValue=0&relatedAddress=TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh",
                     headers=headers)

    parsed_data = json.loads(r.text)

    token_transfers = parsed_data['token_transfers']

    for transfer in token_transfers:
        session = Session()
        dict_ = {
            'quant': transfer['quant'],
            'from_address': transfer['from_address'],
            'to_address': transfer['to_address'],
            'transaction_id': transfer['transaction_id'],
            'tokenAbbr': transfer['tokenInfo']['tokenAbbr']
        }
        if not session.query(Transactions).filter_by(transaction_id=dict_['transaction_id']).first():
            trans = Transactions(
                wallet=WALLET,
                transaction_id=dict_['transaction_id'],
                token_abbr=dict_['tokenAbbr'],
                count=dict_['quant'],
                from_address=dict_['from_address'],
                to_address=dict_['to_address'],
            )

            session.add(trans)
            session.commit()

        session.close()

def main():
    get_data("https://tronscan.org/#/address/TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh/transfers")


if __name__ == '__main__':
    main()
