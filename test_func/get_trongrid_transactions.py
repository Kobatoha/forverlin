import requests


# TRON GRID
api_key = '88b905ca-b432-4f4e-bd6a-09ed49629c4a'
wallet_address = 'TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh'

url = f"https://api.trongrid.io/v1/accounts/{wallet_address}" \
      f"/transactions?only_to=false&only_confirmed=true&limit=50&order_by=block_timestamp,desc"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    transactions = response.json()["data"]
    for transaction in transactions:
        print(transaction)
else:
    print(f"Error: {response.status_code} - {response.text}")
