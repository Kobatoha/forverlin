import requests
import datetime as dt

print(dt.datetime.now().strftime('%H:%M'))
print(dt.datetime.today())


# TRON GRID
api_key = '88b905ca-b432-4f4e-bd6a-09ed49629c4a'
wallet_address = 'TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh'

today = dt.datetime.now().date()

start_of_yesterday = dt.datetime.combine(today, dt.time.min)
end_of_yesterday = dt.datetime.combine(today, dt.time.max)

min_timestamp = int(start_of_yesterday.timestamp() * 1000)
max_timestamp = int(end_of_yesterday.timestamp() * 1000)

url = f"https://api.trongrid.io/v1/accounts/{wallet_address}/transactions/trc20"

params = {
    'only_confirmed': True,
    'min_timestamp': min_timestamp,
    'max_timestamp': max_timestamp,
    'limit': 200
}

headers = {"Authorization": f"Bearer {api_key}"}


response = requests.get(url, params=params, headers=headers)
num = 0

if response.status_code == 200:
    transactions = response.json()["data"]
    for transaction in transactions:
        num += 1
        print(num, transaction)
else:
    print(f"Error: {response.status_code} - {response.text}")
