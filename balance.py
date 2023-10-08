import requests
import json
import asyncio


async def get_balance_trx(wallet_address):
    address = wallet_address

    url = f"https://api.trongrid.io/v1/accounts/{address}"

    response = requests.get(url)

    if response.status_code == 200:
        response_json = json.loads(response.text)
        balance = response_json["data"][0]["balance"]

        return balance

    else:
        print("Ошибка при запросе API")


async def get_balance_usdt(wallet_address):
    address = wallet_address
    url = f'https://apilist.tronscan.org/api/account?address={address}'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        a = 0
        token_balances = data['trc20token_balances']
        for token in token_balances:
            if token['tokenAbbr'] == 'USDT':
                name = token['tokenName']
                symbol = token['tokenAbbr']
                balance = token['balance']
                # print(f'{address}: {name} ({symbol}): {balance[:-6]}.{balance[-6:]}')
                return int(balance)
            else:
                return a

    else:
        print('Error getting wallet balance')
