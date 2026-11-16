import hashlib
import uuid
import requests

# 1. Настройки (должны совпадать с вашим сервером FastAPI)
URL = "http://127.0.0.1:8000/webhook/getpayment"
WEBHOOK_SECRET = "1234"

# 2. Данные тестовой транзакции
payload = {
    "transaction_id": str(uuid.uuid4()),  # Генерируем уникальный ID каждый раз
    "user_id": 1,
    "account_id": 1,
    "amount": 100
}
# 3. Генерируем подпись (логика должна 1-в-1 повторять verify_signature на сервере!)
raw_string = f"{payload['account_id']}{payload['amount']}{payload['transaction_id']}{payload['user_id']}{WEBHOOK_SECRET}"
payload["signature"] = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()

# 4. Отправляем POST-запрос
try:
    response = requests.post(URL, json=payload)
    print(f"Статус ответа: {response.status_code}")
    print(f"Тело ответа: {response.json()}")
except requests.exceptions.ConnectionError:
    print("Ошибка: Не удалось подключиться к серверу. Убедитесь, что FastAPI запущен.")
