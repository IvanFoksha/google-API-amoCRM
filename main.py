import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Импортируем обе наши функции синхронизации
from app.sync_amo_to_sheets import process_webhook
from app.sync_sheets_to_amo import run_sheets_to_amo_sync

# Загружаем переменные окружения
load_dotenv()

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
    Добавляет задачу обработки вебхука в фон, чтобы не блокировать ответ.
    """
    try:
        data = await request.json()
        background_tasks.add_task(process_webhook, data)
        # print("Webhook received:", data) # Временный вывод можно убрать
        return {"status": "success", "message": "Webhook received"}
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": "Invalid data format"}

# --- Блок для ручного тестирования синхронизации ---
# Этот блок больше не нужен, т.к. синхронизация теперь автоматическая
# if __name__ == "__main__":
#     print("Запуск синхронизации в ручном режиме...")
#     asyncio.run(run_sheets_to_amo_sync())
#     print("Синхронизация завершена.")
