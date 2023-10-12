import os
import json
import datetime as dt
import requests

num = 0
account_id = "TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh"
url = f"https://api.trongrid.io/v1/accounts/{account_id}/transactions/trc20"
pages = 77

params = {
    # 'only_to': True,
    # 'only_from': True,
    # 'max_timestamp': dt.datetime.timestamp(dt.datetime.now() - dt.timedelta(hours=6))*1000,
    'only_confirmed': True,
    'limit': 20,
}
transactions_by_day = []

for _ in range(0, pages):
    r = requests.get(url, params=params, headers={"accept": "application/json"})
    params['fingerprint'] = r.json().get('meta', {}).get('fingerprint')

    for tr in r.json().get('data', []):
        num += 1
        symbol = tr.get('token_info', {}).get('symbol')
        fr = tr.get('from')
        to = tr.get('to')
        v = tr.get('value', '')
        dec = -1 * int(tr.get('token_info', {}).get('decimals', '6'))
        f = float(v[:dec] + '.' + v[dec:])
        time_ = dt.datetime.fromtimestamp(float(tr.get('block_timestamp', '')) / 1000)

        if time_.date() not in [d.get('date') for d in transactions_by_day]:
            transactions_by_day.append({'date': time_.date(), 'transactions': []})
        transactions_by_day[[d.get('date') for d in transactions_by_day].index(time_.date())]['transactions'].append(tr)

        print(f"{num:>3} | {time_} | {f:>9.02f} {symbol} | {fr} > {to}")

# создаем папку Reports, если ее нет
if not os.path.exists(os.path.join("../Reports", 'Days')):
    os.makedirs(os.path.join("../Reports", 'Days'))

# сохраняем каждый день в отдельный файл
for day in transactions_by_day:
    print(day)
    date_str = str(day.get('date'))
    file_name = f"{account_id[:3]}_{date_str}.json"
    file_path = os.path.join("../Reports", 'Days', file_name)
    with open(file_path, 'w') as f:
        json.dump(day.get('transactions'), f, indent=4)  # add indent argument to make it readable

