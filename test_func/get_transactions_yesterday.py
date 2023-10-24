import os
import json
import datetime as dt
import requests
import asyncio


async def get_transactions(wallet_address):
    today = dt.datetime.now().date()
    yesterday = today - dt.timedelta(days=1)

    start_of_yesterday = dt.datetime.combine(yesterday, dt.time.min)
    end_of_yesterday = dt.datetime.combine(yesterday, dt.time.max)

    min_timestamp = int(start_of_yesterday.timestamp() * 1000)
    max_timestamp = int(end_of_yesterday.timestamp() * 1000)

    num = 0
    url = f"https://api.trongrid.io/v1/accounts/{wallet_address}/transactions/trc20"
    pages = 100

    params = {
        'only_confirmed': True,
        'min_timestamp': min_timestamp,
        'max_timestamp': max_timestamp,
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
            transaction_id = tr.get('transaction_id')

            if transaction_id not in transactions_by_day:
                transactions_by_day.append({'num': num,
                                            'time': time_,
                                            'value': f,
                                            'symbol': symbol,
                                            'from': fr,
                                            'to': to,
                                            'transaction_id': transaction_id})
                print(f"{num:>3} | {time_} | {f:>9.02f} {symbol} | {fr} > {to} | tr_id: {transaction_id}")

    # создаем папку Reports, если ее нет
    if not os.path.exists(os.path.join("../Reports", 'Days')):
        os.makedirs(os.path.join("../Reports", 'Days'))

    # сохраняем отчет предыдущего дня в отдельный файл
    filename = f"{wallet_address[:3]}_{yesterday.strftime('%Y-%m-%d')}.txt"
    filepath = os.path.join("../Reports/Days", filename)

    with open(filepath, 'w') as f:
        for day in transactions_by_day:
            for tr in day:
                f.write(
                    f"{tr['transaction_id']} | {tr['time']} | {tr['value']:.2f} {tr['symbol']} | {tr['from']} > {tr['to']}\n")


asyncio.run(get_transactions('THownc4gcVVvWm9yr51s9ZSkFzVQYRfKvT'))
