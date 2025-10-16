import os
from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Импортируем (пока что несуществующую) функцию обработки вебхука
# from app.sync_amo_to_sheets import process_webhook

app = FastAPI(title="AmoCRM <-> Google Sheets Sync")


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности сервиса."""
    return {"status": "ok", "message": "Service is running"}


@app.post("/webhook/amocrm")
async def handle_amocrm_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Эндпоинт для приема вебхуков от amoCRM.
    Добавляет задачу обработки вебхука в фон, чтобы не блокировать ответ.
    """
    try:
        data = await request.json()
        # background_tasks.add_task(process_webhook, data)
        print("Webhook received:", data) # Временный вывод для отладки
        return {"status": "success", "message": "Webhook received"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": "Invalid data format"}
