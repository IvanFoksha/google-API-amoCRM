import os
import httpx
from typing import Optional, Dict, Any

class AmoCRMClient:
    """Асинхронный клиент для работы с API amoCRM v4."""

    def __init__(self):
        self.subdomain = os.getenv("AMOCRM_SUBDOMAIN")
        self.token = os.getenv("AMOCRM_INTEGRATION_TOKEN")

        if not self.subdomain or not self.token:
            raise ValueError("AMOCRM_SUBDOMAIN и AMOCRM_INTEGRATION_TOKEN должны быть установлены.")

        self.base_url = f"https://{self.subdomain}.amocrm.ru/api/v4"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """Вспомогательный метод для выполнения асинхронных запросов."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, f"{self.base_url}/{endpoint}", headers=self.headers, params=params, json=data
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Ошибка API amoCRM: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                print(f"Произошла ошибка при запросе к amoCRM: {e}")
        return None

    async def create_lead(self, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создает новую сделку."""
        return await self._make_request("POST", "leads", data=[lead_data])

    async def update_lead(self, lead_id: int, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновляет существующую сделку."""
        return await self._make_request("PATCH", f"leads/{lead_id}", data=lead_data)

    @staticmethod
    def format_custom_fields(fields: Dict[str, Any]) -> list:
        """
        Форматирует кастомные поля в формат, понятный API amoCRM.
        Пример: {"Телефон": "12345", "Email": "test@test.com"}
        """
        custom_fields = []
        # ID полей нужно будет получить из вашего аккаунта amoCRM
        field_id_map = {
            "Телефон": 225341,  # Замените на реальные ID
            "Email": 225343,    # Замените на реальные ID
        }
        for name, value in fields.items():
            if name in field_id_map:
                custom_fields.append({
                    "field_id": field_id_map[name],
                    "values": [{"value": value}]
                })
        return custom_fields
