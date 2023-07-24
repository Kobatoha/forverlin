import requests
import gzip
from io import BytesIO
from bs4 import BeautifulSoup
import json
from config import WALLET
import datetime


def get_data(url):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    come_in = WALLET

    r = requests.get("https://apilist.tronscanapi.com/api/token_trc20/transfers?limit=50&start=0&sort=-timestamp&count=true&filterTokenValue=0&relatedAddress=TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh",
                     headers=headers)

    parsed_data = json.loads(r.text)

    token_transfers = parsed_data['token_transfers']

    for transfer in token_transfers:
        dict_ = {
            'quant': transfer['quant'],
            'from_address': transfer['from_address'],
            'to_address': transfer['to_address'],
            'transaction_id': transfer['transaction_id'],
            'tokenAbbr': transfer['tokenInfo']['tokenAbbr']
        }

    with open('usdt.txt', 'r') as file:
        data = file.readlines()
        existing_ids = set()
        for line in data:
            transfer = json.loads(line)
            existing_ids.add(transfer['transaction_id'])

    with open('usdt.txt', 'a') as file:
        for transfer in token_transfers:
            now = datetime.datetime.now().strftime('%H:%M')
            dict_ = {
                'tokenAbbr': transfer['tokenInfo']['tokenAbbr'],
                'quant': transfer['quant'],
                'from_address': transfer['from_address'],
                'to_address': transfer['to_address'],
                'transaction_id': transfer['transaction_id'],
                'time': now,
                'send_message': False
            }
            if transfer['to_address'] == come_in and len(transfer['quant']) > 6 and transfer['tokenInfo']['tokenAbbr'] == 'USDT':
                if dict_['transaction_id'] not in existing_ids:
                    json.dump(dict_, file)
                    file.write('\n')
                    existing_ids.add(dict_['transaction_id'])
                    print('add record')

    with open('json.txt', 'w') as file:
        file.write(json.dumps(parsed_data, indent=4))


def main():
    get_data("https://tronscan.org/#/address/TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh/transfers")


@dp.message_handler(commands=['usdt'])
async def send_usdt(message: types.Message):
    main()
    with open('usdt.txt', 'r') as file:
        data = file.readlines()
        for line in data:
            transfer = json.loads(line)
            count = transfer['quant']
            if count[-6:] == '000000':
                count = count[:-9] + ',' + count[-9:-6]
            else:
                count = count[:-9] + ',' + count[-9:-6] + '.' + count[-6:]
            await message.answer(f"+{count} usdt in {transfer['time']}\n")



if __name__ == '__main__':
    main()
