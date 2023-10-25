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
    'order_by': 'block_timestamp,desc',
    'limit': 200
}

headers = {"Authorization": f"Bearer {api_key}"}


response = requests.get(url, params=params, headers=headers)
num = 0
reports = []

if response.status_code == 200:
    transactions = response.json()["data"]
    for tr in transactions:
        num += 1
        symbol = tr.get('token_info', {}).get('symbol')
        fr = tr.get('from')
        to = tr.get('to')
        v = tr.get('value', '')
        dec = -1 * int(tr.get('token_info', {}).get('decimals', '6'))
        f = float(v[:dec] + '.' + v[dec:])
        time_ = dt.datetime.fromtimestamp(float(tr.get('block_timestamp', '')) / 1000)
        if fr != wallet_address:
            reports.append(f"{time_.strftime('%H:%M')}: +{f:,.02f} from {fr[:3]}_{fr[-3:]}")
        else:
            reports.append(f"{time_.strftime('%H:%M')}: -{f:,.02f} to {to[:3]}_{to[-3:]}")

else:
    print(f"Error: {response.status_code} - {response.text}")

for i in reports:
    print(i)

