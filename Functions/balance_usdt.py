import requests


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
            print(f'{address}: {name} ({symbol}): {balance[:-9]},{balance[-9:-6]}.{balance[-6:]}')
else:
    print('Error getting wallet balance')
