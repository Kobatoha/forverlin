from tronapi import Tron


# Создаем экземпляр класса Tron с указанием узла блокчейна
tron = Tron("https://api.trongrid.io")

# Адрес кошелька, данные транзакций которого необходимо получить
wallet_address = "Txxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Получаем список транзакций кошелька
transactions = tron.get_transactions_from_address(wallet_address)

# Выводим информацию о каждой транзакции
for tx in transactions:
    print("Hash:", tx["txID"])
    print("From:", tx["raw_data"]["contract"][0]["parameter"]["value"]["owner_address"])
    print("To:", tx["raw_data"]["contract"][0]["parameter"]["value"]["to_address"])
    print("Amount:", tx["raw_data"]["contract"][0]["parameter"]["value"]["amount"])
    print("Timestamp:", tron.from_timestamp(tx["raw_data"]["timestamp"]))
    print("--------------------")
