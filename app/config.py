import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла один раз в этом месте.
load_dotenv()

# --- Настройки amoCRM ---
AMOCRM_SUBDOMAIN = os.getenv("AMOCRM_SUBDOMAIN")
AMOCRM_INTEGRATION_TOKEN = os.getenv("AMOCRM_INTEGRATION_TOKEN")

# --- Настройки Google ---
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Проверка, что все необходимые переменные были загружены
if not all([AMOCRM_SUBDOMAIN, AMOCRM_INTEGRATION_TOKEN, GOOGLE_SHEET_ID, GOOGLE_APPLICATION_CREDENTIALS]):
    missing = [
        var for var, val in locals().items() 
        if var.isupper() and not val
    ]
    raise ImportError(f"КРИТИЧЕСКАЯ ОШИБКА: Не найдены переменные окружения: {', '.join(missing)}. Проверьте ваш .env файл.")
