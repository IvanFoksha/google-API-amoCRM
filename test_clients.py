import asyncio
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Убедимся, что PYTHONPATH корректен для импорта из app
sys.path.append('.')

from app.google_sheets_client import GoogleSheetsClient
from app.amocrm_client import AmoCRMClient

async def main():
    """Главная функция для тестирования клиентов с расширенным выводом."""

    print("--- Проверка переменных окружения ---")
    google_sheet_id = os.getenv("GOOGLE_SHEET_NAME")
    google_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    amocrm_subdomain = os.getenv("AMOCRM_SUBDOMAIN")
    amocrm_token = os.getenv("AMOCRM_INTEGRATION_TOKEN")

    # Вывод используемых переменных для сверки
    print(f"ID таблицы (GOOGLE_SHEET_NAME): '{google_sheet_id}'")
    print(f"Путь к ключу (GOOGLE_APPLICATION_CREDENTIALS): '{google_creds_path}'")
    print(f"Субдомен amoCRM (AMOCRM_SUBDOMAIN): '{amocrm_subdomain}'")
    print(f"Токен amoCRM (AMOCRM_INTEGRATION_TOKEN): '{str(amocrm_token)[:10]}...' (проверяем только первые 10 символов)")

    print("\n--- 1. Тестирование клиента Google Sheets ---")
    if not google_sheet_id or not google_creds_path:
        print("ОШИБКА: GOOGLE_SHEET_NAME или GOOGLE_APPLICATION_CREDENTIALS не установлены в .env файле.")
    else:
        # === НАЧАЛО НОВОЙ ПРОВЕРКИ ===
        print(f"Попытка прочитать файл ключа '{google_creds_path}' напрямую...")
        try:
            with open(google_creds_path, 'r') as f:
                content = f.read()
                print("УСПЕХ: Файл ключа успешно прочитан. Длина содержимого:", len(content), "байт.")
        except Exception as e:
            print(f"КРИТИЧЕСКАЯ ОШИБКА ПРИ ЧТЕНИИ ФАЙЛА: {e}")
            print("Python не может получить доступ к файлу. Проблема в правах доступа на уровне файловой системы.")
        # === КОНЕЦ НОВОЙ ПРОВЕРКИ ===

        if not os.path.exists(google_creds_path):
            print(f"КРИТИЧЕСКАЯ ОШИБКА: Файл ключа '{google_creds_path}' не найден! Проверьте путь в .env и наличие файла.")
        else:
            try:
                print("Инициализация клиента Google Sheets...")
                gs_client = GoogleSheetsClient(sheet_id=google_sheet_id)
                print("Попытка прочитать данные из таблицы...")
                records = gs_client.get_all_records()
                if records is not None:
                    print(f"УСПЕХ: Прочитано {len(records)} строк из таблицы.")
                    print("Первые 5 строк:", records[:5])
                else:
                    print("ОШИБКА: Данные не получены. Возможные причины: неверное имя листа (должно быть 'Лист1') или таблица пуста.")
            except Exception as e:
                print(f"ОШИБКА при работе с Google Sheets: {e}")
                print(f"Тип ошибки: {type(e).__name__}, Полное представление: {repr(e)}")

    print("\n--- 2. Тестирование клиента amoCRM ---")
    if not amocrm_subdomain or not amocrm_token:
        print("ОШИБКА: AMOCRM_SUBDOMAIN или AMOCRM_INTEGRATION_TOKEN не установлены в .env файле.")
    else:
        try:
            print(f"Инициализация клиента amoCRM для субдомена: {amocrm_subdomain}...")
            amo_client = AmoCRMClient()
            
            print("Попытка создать тестовую сделку...")
            create_payload = {"name": "Тестовая сделка из скрипта", "price": 12345}
            response_data = await amo_client.create_lead(create_payload)
            
            if response_data and "_embedded" in response_data:
                lead_id = response_data["_embedded"]["leads"][0]["id"]
                print(f"УСПЕХ: Создана сделка с ID: {lead_id}")
            else:
                print("ОШИБКА: Не удалось создать сделку. Ответ от API:", response_data)
        except Exception as e:
            print(f"ОШИБКА при работе с amoCRM: {e}")

if __name__ == "__main__":
    asyncio.run(main())
