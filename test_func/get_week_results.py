import json
import datetime as dt

file_path = "../Reports/Weeks/TGz_2023-10-02_2023-10-08.json"
account_id = "TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh"

with open(file_path, 'r') as f:
    transactions = json.load(f)

num = 0
print('№ | USDT | 2023-10-02 - 2023-10-08\n', '_' * 30)
for tr in transactions:
    num += 1
    symbol = tr.get('token_info', {}).get('symbol')
    fr = tr.get('from')
    to = tr.get('to')
    v = tr.get('value', '')
    dec = -1 * int(tr.get('token_info', {}).get('decimals', '6'))
    f = float(v[:dec] + '.' + v[dec:])
    time_ = str(dt.datetime.fromtimestamp(float(tr.get('block_timestamp', '')) / 1000))
    if to == account_id:
        print(f"{num} | {f:+9.02f} | [{fr[:3]}...{fr[-3:]}] > [{to[:3]}...{to[-3:]}]")
    else:
        print(f"{num} | {-f:9.02f} | [{fr[:3]}...{fr[-3:]}] > [{to[:3]}...{to[-3:]}]")
