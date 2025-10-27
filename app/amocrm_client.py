import os
import httpx
from typing import Optional, Dict, Any, Union, List

class AmoCRMClient:
    """Асинхронный клиент для работы с API amoCRM v4."""

    def __init__(self, subdomain: str, token: str):
        if not subdomain or not token:
            raise ValueError("Субдомен и токен amoCRM должны быть предоставлены.")

        self.base_url = f"https://{subdomain}.amocrm.ru/api/v4/"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Union[Dict, List]] = None,
        params: Optional[Dict] = None,
    ) -> Optional[Dict[str, Any]]:
        """Внутренний метод для выполнения запросов к API."""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method, url, json=data, params=params, headers=self.headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"Ошибка API amoCRM: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                print(f"Произошла ошибка при запросе к amoCRM: {e}")
        return None

    async def get_lead(self, lead_id: int) -> Optional[Dict[str, Any]]:
        """Получает данные сделки по ее ID с дополнительными полями."""
        params = {"with": "contacts"}
        return await self._make_request("GET", f"leads/{lead_id}", params=params)

    async def create_lead(self, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Создает одну новую сделку."""
        return await self._make_request("POST", "leads", data=[lead_data])

    async def update_lead(self, lead_id: int, lead_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Обновляет существующую сделку."""
        return await self._make_request("PATCH", f"leads/{lead_id}", data=lead_data)

    async def create_note(self, lead_id: int, note_text: str) -> Optional[Dict[str, Any]]:
        """Создает текстовое примечание к сделке."""
        note_data = [{
            "note_type": "common",
            "params": {
                "text": note_text
            }
        }]
        return await self._make_request("POST", f"leads/{lead_id}/notes", data=note_data)

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
