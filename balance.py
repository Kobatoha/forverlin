import requests
import json

address = "TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh"

url = f"https://api.trongrid.io/v1/accounts/{address}"

response = requests.get(url)

if response.status_code == 200:
    response_json = json.loads(response.text)
    balance = str(response_json["data"][0]["balance"])
    print(f"{address}: TRX (TRX): {balance[:-6]}.{balance[-6:]}")

    # Получаем цену TRX в долларах
    url_trx_price = "https://api.coingecko.com/api/v3/simple/price?ids=tron&vs_currencies=usd"
    response_trx_price = requests.get(url_trx_price)
    if response_trx_price.status_code == 200:
        trx_price = response_trx_price.json()["tron"]["usd"]
        balance_usd = float(balance) * trx_price
        print(f"{address}: TRX (TRX) - ${balance_usd:.2f} (price: {trx_price})")
    else:
        print("Ошибка при запросе API для получения цены TRX в долларах")

else:
    print("Ошибка при запросе API")

# Просмотр баланса только trx и usdt
address = 'TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh'
url = f'https://apilist.tronscan.org/api/account?address={address}'

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    token_balances = data['trc20token_balances']
    for token in token_balances:
        if token['tokenAbbr'] == 'USDT':
            name = token['tokenName']
            symbol = token['tokenAbbr']
            balance = token['balance']
            print(f'{address}: {name} ({symbol}): {balance[:-6]}.{balance[-6:]}')

            # Получаем цену USDT в долларах
            url_usdt_price = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"
            response_usdt_price = requests.get(url_usdt_price)
            if response_usdt_price.status_code == 200:
                usdt_price = response_usdt_price.json()["tether"]["usd"]
                balance_usd = float(balance) * usdt_price
                print(f"{address}: {name} ({symbol}) - ${balance_usd:.2f} (price: {usdt_price})")
            else:
                print("Ошибка при запросе API для получения цены USDT в долларах")

else:
    print('Error getting wallet balance')
