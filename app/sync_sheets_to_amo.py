import os
import asyncio
from app.google_sheets_client import GoogleSheetsClient
from app.amocrm_client import AmoCRMClient

# ID воронки и статуса, куда будут падать новые сделки.
# ЗАМЕНИТЕ ИХ НА ВАШИ РЕАЛЬНЫЕ ID.
PIPELINE_ID = 10203662 # Пример
STATUS_ID = 63688174   # Пример


def _prepare_lead_data(row: dict) -> dict:
    """Формирует тело запроса для создания/обновления сделки из строки таблицы."""
    return {
        "name": f"Сделка по {row.get('Имя', 'N/A')}",
        "price": int(row.get("Сумма", 0)) if str(row.get("Сумма")).isdigit() else 0,
    }

def _prepare_note_text(row: dict, is_update: bool = False) -> str:
    """Формирует текст примечания с контактными данными."""
    header = "Обновленные контактные данные:" if is_update else "Контактные данные из Google Sheets:"
    phone = row.get('Телефон', 'не указан')
    email = row.get('Email', 'не указан')
    return f"{header}\nТелефон: {phone}\nEmail: {email}"


async def run_sheets_to_amo_sync():
    """
    Основная функция синхронизации: читает данные из Google Sheets
    и обновляет/создает сделки в amoCRM, добавляя контакты в примечания.
    """
    print("--- Запуск синхронизации Google Sheets -> amoCRM ---")
    
    gs_client = GoogleSheetsClient(sheet_id=os.getenv("GOOGLE_SHEET_NAME"))
    amo_client = AmoCRMClient()
    
    records = gs_client.get_all_records()
    if not records:
        print("В таблице нет данных для синхронизации.")
        return

    try:
        header = gs_client.get_worksheet().row_values(1)
        lead_id_col_index = header.index("lead_id") + 1
    except (ValueError, AttributeError):
        print("КРИТИЧЕСКАЯ ОШИБКА: В таблице отсутствует колонка 'lead_id'.")
        return

    total_rows = len(records)
    print(f"Найдено {total_rows} строк для обработки.")

    for i, row in enumerate(records):
        row_num = i + 2
        lead_id = row.get("lead_id")
        
        print(f"[{row_num-1}/{total_rows}] Обработка строки: {row}")

        lead_data = _prepare_lead_data(row)
        
        if lead_id:
            print(f"  -> ID {lead_id} найден. Обновление сделки и добавление примечания...")
            await amo_client.update_lead(int(lead_id), lead_data)
            note_text = _prepare_note_text(row, is_update=True)
            await amo_client.create_note(int(lead_id), note_text)
        else:
            print("  -> ID не найден. Создание новой сделки...")
            lead_data["pipeline_id"] = PIPELINE_ID
            lead_data["status_id"] = STATUS_ID
            
            response = await amo_client.create_lead(lead_data)
            
            if response and "_embedded" in response and "leads" in response["_embedded"]:
                new_lead_id = response["_embedded"]["leads"][0]["id"]
                print(f"  -> Сделка создана, ID: {new_lead_id}. Добавление примечания...")
                
                note_text = _prepare_note_text(row)
                await amo_client.create_note(new_lead_id, note_text)
                
                print("  -> Запись ID в таблицу...")
                gs_client.update_cell(row_num, lead_id_col_index, str(new_lead_id))
            else:
                print(f"  -> ОШИБКА: Не удалось создать сделку для строки {row_num}.")
                
        await asyncio.sleep(0.5)

    print("--- Синхронизация Google Sheets -> amoCRM завершена ---")
