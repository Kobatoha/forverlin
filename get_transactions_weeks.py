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
transactions_by_week = []

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

        if time_.date() not in [d.get('date') for d in transactions_by_week]:
            transactions_by_week.append({'week_start': (time_.date() - dt.timedelta(
                days=time_.weekday())).strftime('%Y-%m-%d'), 'transactions': [tr]})

        transactions_by_week[[d.get('week_start') for d in transactions_by_week].index(
            (time_.date() - dt.timedelta(days=time_.weekday())).strftime('%Y-%m-%d'))]['transactions'].append(tr)

        print(f"{num:>3} | {time_} | {f:>9.02f} {symbol} | {fr} > {to}")

if not os.path.exists(os.path.join("Reports", 'Weeks')):
    os.makedirs(os.path.join("Reports", 'Weeks'))

for week in transactions_by_week:
    week_start = week.get('week_start')
    week_end = (dt.datetime.strptime(week_start, '%Y-%m-%d') + dt.timedelta(days=6)).strftime('%Y-%m-%d')
    file_name = f"{account_id[:3]}_{week_start}_{week_end}.json"
    file_path = os.path.join("Reports", 'Weeks', file_name)
    transactions = week.get('transactions')
    print(f"Writing {len(transactions)} transactions to {file_path}")

    # Check if file already exists and append transactions if it does
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            existing_transactions = json.load(f)
        existing_transactions.extend(transactions)
        transactions = existing_transactions

    with open(file_path, 'w') as f:
        json.dump(transactions, f, indent=4)