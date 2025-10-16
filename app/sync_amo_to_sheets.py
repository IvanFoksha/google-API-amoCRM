import os
from app.google_sheets_client import GoogleSheetsClient

# Соответствие между ID полей в amoCRM и названиями колонок в Google Sheets
# Это нужно, чтобы скрипт знал, какую ячейку обновлять.
# ID статуса и воронки вы уже знаете.
STATUS_FIELD_ID = "status_id"  # Это не ID, а системное имя поля статуса
PIPELINE_FIELD_ID = "pipeline_id" # Системное имя поля воронки
PRICE_FIELD_ID = "price" # Системное имя поля бюджета

# Важно: gspread ищет колонки по названию из первой строки (заголовка)
COLUMN_MAPPING = {
    STATUS_FIELD_ID: "Статус",
    PIPELINE_FIELD_ID: "Воронка",
    PRICE_FIELD_ID: "Сумма",
}


def _find_column_index(header: list, column_name: str) -> int:
    """Находит индекс колонки по ее имени (1-based)."""
    try:
        return header.index(column_name) + 1
    except ValueError:
        return -1


async def process_webhook(data: dict):
    """
    Обрабатывает входящий вебхук от amoCRM.
    """
    print("--- Обработка вебхука от amoCRM ---")
    
    # Вебхуки могут приходить по разным событиям, нас интересует обновление сделки
    # Данные по сделке обычно лежат в 'leads' -> 'update'
    try:
        lead_info = data["leads"]["update"][0]
        lead_id = int(lead_info["id"])
        print(f"Получено обновление для сделки ID: {lead_id}")
    except (KeyError, IndexError):
        print("Вебхук не содержит данных об обновлении сделки. Пропуск.")
        return

    gs_client = GoogleSheetsClient(sheet_id=os.getenv("GOOGLE_SHEET_NAME"))
    worksheet = gs_client.get_worksheet()
    if not worksheet:
        return

    # Находим строку в таблице по lead_id
    row_number = gs_client.find_row_by_id(lead_id)
    if not row_number:
        print(f"Сделка с ID {lead_id} не найдена в таблице. Пропуск.")
        return

    print(f"Найдена строка {row_number} для обновления.")
    header = worksheet.row_values(1)

    # Проходим по всем полям, которые изменились в сделке
    for field_name, column_to_update in COLUMN_MAPPING.items():
        if field_name in lead_info:
            new_value = lead_info[field_name]
            
            # Для статуса и воронки вебхук часто присылает массив объектов,
            # нам нужен ID из нового значения
            if isinstance(new_value, list) and new_value:
                new_value = new_value[0].get("id", new_value)

            col_index = _find_column_index(header, column_to_update)
            if col_index != -1:
                print(f"  -> Обновление колонки '{column_to_update}' на значение '{new_value}'")
                gs_client.update_cell(row_number, col_index, str(new_value))
            else:
                print(f"  -> ПРЕДУПРЕЖДЕНИЕ: Колонка '{column_to_update}' не найдена в таблице.")

    print(f"--- Обработка вебхука для сделки {lead_id} завершена ---")
