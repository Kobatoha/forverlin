import requests
import datetime

# Адрес кошелька
wallet_address = "TGzNdQBmFqisqsbSwEbBunoBegVQsYALRh"

# URL API TronGrid
url = f"https://api.trongrid.io/v1/accounts/{wallet_address}/transactions/trc20?only_confirmed=true&limit=10"

# API ключ (необязательно)
api_key = "88b905ca-b432-4f4e-bd6a-09ed49629c4a"

# Заголовки запроса
headers = {
    "Content-Type": "application/json",
    "TRON-PRO-API-KEY": api_key
}

# Отправляем GET запрос к API TronGrid
response = requests.get(url, headers=headers)

# Получаем JSON-ответ
data = response.json()

# Обрабатываем данные
for tx in data["data"]:
    # Адрес отправителя
    from_address = tx["from"]

    # Адрес получателя
    to_address = tx["to"]

    # Название монеты
    coin_name = tx["tokenInfo"]["name"]

    # Количество монет
    amount = tx["value"]

    # Дата и время транзакции
    timestamp = int(tx["timestamp"] / 1000)
    date_time = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    # Выводим информацию о транзакции
    print(f"From: {from_address}")
    print(f"To: {to_address}")
    print(f"Coin: {coin_name}")
    print(f"Amount: {amount}")
    print(f"Date: {date_time.split()[0]}")
    print(f"Time: {date_time.split()[1]}")
    print("--------------")