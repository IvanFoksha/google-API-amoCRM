import os
import gspread

# Этот метод аутентификации, как в вашем примере с Битрикс,
# должен быть более устойчивым в окружении WSL.
# Он использует устаревшую, но надежную библиотеку oauth2client.

class GoogleSheetsClient:
    """Класс для взаимодействия с Google Sheets API."""

    def __init__(self, sheet_id: str):
        self.sheet_id = sheet_id
        self.creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not self.sheet_id or not self.creds_path:
            raise ValueError("Переменные GOOGLE_SHEET_NAME или GOOGLE_APPLICATION_CREDENTIALS не установлены.")
            
        if not os.path.exists(self.creds_path):
            raise FileNotFoundError(f"Файл ключа '{self.creds_path}' не найден.")

        self.client = self._connect()
        if self.client:
            self.spreadsheet = self.client.open_by_key(self.sheet_id)
        else:
            self.spreadsheet = None

    def _connect(self):
        """Инициализирует подключение к Google Sheets."""
        try:
            client = gspread.service_account(filename=self.creds_path)
            print("Успешное подключение к Google Sheets.")
            return client
        except Exception as e:
            print(f"Не удалось подключиться к Google Sheets: {e}")
            return None

    def get_worksheet(self, sheet_name: str = "Лист1"):
        """Получает объект рабочего листа по его имени."""
        if not self.spreadsheet:
            return None
        try:
            return self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            print(f"Лист с именем '{sheet_name}' не найден.")
            return None

    def get_all_records(self, sheet_name: str = "Лист1"):
        """Возвращает все строки из листа в виде словаря."""
        worksheet = self.get_worksheet(sheet_name)
        if worksheet:
            return worksheet.get_all_records()
        return []

    def update_cell(self, row: int, col: int, value: str, sheet_name: str = "Лист1"):
        """Обновляет значение в конкретной ячейке."""
        worksheet = self.get_worksheet(sheet_name)
        if worksheet:
            worksheet.update_cell(row, col, value)
            print(f"Ячейка ({row}, {col}) обновлена значением '{value}'.")

    def find_row_by_id(self, lead_id: int, id_column_name: str = "lead_id", sheet_name: str = "Лист1"):
        """Находит номер строки по ID сделки."""
        worksheet = self.get_worksheet(sheet_name)
        if not worksheet:
            return None
        try:
            # gspread.CellNotFound - это нормальное поведение, обрабатываем его.
            cell = worksheet.find(str(lead_id), in_column=1) # Ищем в первой колонке
            return cell.row if cell else None
        except gspread.exceptions.CellNotFound:
            return None # Явный возврат, если ячейка не найдена
        except Exception as e:
            print(f"Произошла ошибка при поиске lead_id={lead_id}: {e}")
            return None
