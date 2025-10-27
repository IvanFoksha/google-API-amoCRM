import asyncio
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Импортируем обе наши функции синхронизации
from app.sync_amo_to_sheets import process_webhook
from app.sync_sheets_to_amo import run_sheets_to_amo_sync

# Загрузка переменных окружения теперь происходит в app.config

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения FastAPI.
    Запускает и останавливает планировщик.
    """
    # Запускаем синхронизацию один раз при старте
    # и затем каждые 5 минут
    scheduler.add_job(run_sheets_to_amo_sync, 'interval', minutes=5, id="sheets_to_amo_job")
    scheduler.start()
    print("Планировщик запущен: синхронизация 'Sheets -> amoCRM' каждые 5 минут.")
    yield
    scheduler.shutdown()
    print("Планировщик остановлен.")

app = FastAPI(
    title="AmoCRM <-> Google Sheets Sync",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности сервиса."""
    return {"status": "ok", "message": "Service is running"}


@app.post("/webhook/amocrm")
async def handle_amocrm_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Эндпоинт для приема вебхуков от amoCRM.
    Обрабатывает данные как в формате JSON, так и в виде данных формы.
    """
    data = None
    content_type = request.headers.get('content-type', '')

    if "application/json" in content_type:
        try:
            data = await request.json()
        except Exception:
            pass  # Ошибка будет обработана ниже

    elif "application/x-www-form-urlencoded" in content_type:
        form_data = await request.form()
        
        reconstructed_data = {}
        for key, value in form_data.items():
            match = re.match(r"(\w+)\[(\w+)\]\[(\d+)\]\[(\w+)\]", key)
            if match:
                top_key, event_type, index_str, field_name = match.groups()
                index = int(index_str)
                
                reconstructed_data.setdefault(top_key, {}).setdefault(event_type, [])
                
                while len(reconstructed_data[top_key][event_type]) <= index:
                    reconstructed_data[top_key][event_type].append({})
                
                reconstructed_data[top_key][event_type][index][field_name] = value
        data = reconstructed_data

    if data:
        background_tasks.add_task(process_webhook, data)
        return {"status": "accepted"}
    else:
        # В случае, если данные не распознаны, логируем и возвращаем ошибку
        body = await request.body()
        print(f"CRITICAL: Could not parse webhook data. Raw body: {body.decode('utf-8')}")
        return {"status": "error", "message": "Could not parse webhook data"}


# Блок для ручного запуска был убран. 
# Теперь файл предназначен для запуска через uvicorn в качестве сервера.
