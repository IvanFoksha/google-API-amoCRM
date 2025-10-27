import os
from app.google_sheets_client import GoogleSheetsClient
from app.amocrm_client import AmoCRMClient
from app.config import (
    GOOGLE_SHEET_ID,
    GOOGLE_APPLICATION_CREDENTIALS,
    AMOCRM_SUBDOMAIN,
    AMOCRM_INTEGRATION_TOKEN
)

# Карта для сопоставления полей amoCRM и колонок в Google Sheets.
# При необходимости можно расширить.
COLUMN_MAPPING = {
    'status': 'Статус',
    'price': 'Сумма',
}

async def _update_sheet_row(gs_client: GoogleSheetsClient, row_index: int, updates: dict):
    """Обновляет ячейки в строке на основе словаря 'updates'."""
    try:
        header = gs_client.get_worksheet_header()
        for field_name, new_value in updates.items():
            if field_name not in COLUMN_MAPPING:
                continue

            column_name = COLUMN_MAPPING[field_name]
            if column_name in header:
                col_index = header.index(column_name) + 1
                gs_client.update_cell(row_index, col_index, str(new_value))
    except Exception as e:
        print(f"  -> Ошибка при обновлении строки {row_index} в таблице: {e}")


async def process_webhook(data: dict):
    """
    Обрабатывает входящий вебхук от amoCRM.
    Интересуют только события обновления сделки.
    """
    print(f"--- Получен вебхук от amoCRM: {list(data.keys())}")

    # Убеждаемся, что это событие обновления сделки, которое нас интересует
    if 'leads' not in data or ('update' not in data['leads'] and 'add' not in data['leads']):
        print("  -> Событие не является обновлением/добавлением сделки, игнорируем.")
        return

    event_type = 'update' if 'update' in data['leads'] else 'add'
    lead_info = data['leads'][event_type][0]
    lead_id = int(lead_info.get('id', 0))

    if not lead_id:
        return

    print(f"  -> Обработка обновления для сделки ID: {lead_id}")

    gs_client = GoogleSheetsClient(
        sheet_id=GOOGLE_SHEET_ID,
        creds_path=GOOGLE_APPLICATION_CREDENTIALS
    )
    amo_client = AmoCRMClient(
        subdomain=AMOCRM_SUBDOMAIN,
        token=AMOCRM_INTEGRATION_TOKEN
    )

    # Ищем соответствующую строку в Google Sheets
    row_index, _ = gs_client.find_row_by_id(lead_id)
    if not row_index:
        print(f"  -> Сделка с ID {lead_id} не найдена в таблице. Возможно, она была создана не через интеграцию.")
        return

    # Запрашиваем актуальные данные по сделке, чтобы получить имена, а не ID
    full_lead_data = await amo_client.get_lead(lead_id)
    if not full_lead_data:
        print(f"  -> Не удалось получить детали по сделке ID {lead_id} от amoCRM.")
        return

    # Готовим словарь с обновлениями
    updates_to_make = {}
    
    # Обновление статуса (этапа)
    status_info = full_lead_data.get('_embedded', {}).get('statuses', [])
    if status_info:
        updates_to_make['status'] = status_info[0].get('name', 'N/A')

    # Обновление суммы
    if 'price' in full_lead_data:
        updates_to_make['price'] = full_lead_data.get('price', 0)

    if not updates_to_make:
        print("  -> В обновлении не было данных для синхронизации (статус, сумма).")
        return

    print(f"  -> Найдены обновления для таблицы: {updates_to_make}")
    await _update_sheet_row(gs_client, row_index, updates_to_make)
    print(f"--- Обработка вебхука для сделки {lead_id} завершена ---")
