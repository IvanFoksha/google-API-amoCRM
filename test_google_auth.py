import os
import sys
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

# Загружаем .env
load_dotenv()

print("--- Минимальный тест библиотеки google-auth ---")

# 1. Выводим информацию о системном окружении
print(f"Версия Python: {sys.version}")
print(f"Переменная окружения HOME: {os.getenv('HOME')}")
print(f"Переменная окружения TEMP: {os.getenv('TEMP')}")
print(f"Переменная окружения TMPDIR: {os.getenv('TMPDIR')}")

# 2. Получаем путь к ключу из .env
creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
print(f"Используется файл ключа: {creds_path}")

if not creds_path or not os.path.exists(creds_path):
    print("\nКРИТИЧЕСКАЯ ОШИБКА: Файл ключа не найден. Проверьте .env и путь.")
    sys.exit(1)

# 3. Определяем scope (области доступа)
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
print(f"Используются scope: {scope}")

# 4. Пытаемся создать объект учетных данных
try:
    print("\nПопытка создать объект учетных данных...")
    creds = Credentials.from_service_account_file(creds_path, scopes=scope)
    print("\nУСПЕХ! Объект учетных данных успешно создан.")
    print("Это означает, что аутентификация с помощью JSON-ключа работает корректно.")
    print(f"Email сервисного аккаунта: {creds.service_account_email}")

except Exception as e:
    print(f"\nПРОВАЛ: Произошла ошибка при создании учетных данных.")
    print(f"Тип ошибки: {type(e).__name__}")
    print(f"Детали ошибки: {repr(e)}")
    print("\nЭто подтверждает, что проблема находится внутри библиотеки google-auth и вашего окружения WSL.")
