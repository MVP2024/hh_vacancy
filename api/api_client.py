from typing import Any, Dict, List, Optional, Union

import requests

from logger.logger import setup_logger


class HeadHunterAPI:
    """
    Класс для взаимодействия с API HeadHunter.
    """

    def __init__(
        self,
        requests_lib: Optional[Any] = None,
    ) -> None:
        """
        Инициализирует экземпляр класса HeadHunterAPI.

        Args:
            requests_lib: Библиотека для выполнения HTTP-запросов (по умолчанию `requests`).
        """
        self._requests = requests_lib or requests
        self.logger = setup_logger(__name__)

        self._headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    def get_vacancies(self, search_query: str, per_page: int = 50) -> List[Dict[str, Any]]:
        """
        Поиск вакансий с использованием публичного API.

        Args:
            search_query: Текст поискового запроса.
            per_page: Количество вакансий на странице.

        Returns:
            Список словарей с информацией о вакансиях.
        """
        self.logger.info(f"Начало поиска вакансий. Запрос: {search_query}, кол-во на странице: {per_page}")
        vacancies: List[Dict[str, Any]] = []

        try:
            self.logger.debug("Попытка использовать публичный API")
            vacancies = self._get_public_api_vacancies(search_query, per_page)
            if vacancies:
                self.logger.info(f"Найдено вакансий: {len(vacancies)}")
                return vacancies
        except Exception as public_api_error:
            self.logger.warning(f"Ошибка публичного API: {public_api_error}")

        # Если ни один API не сработал
        if not vacancies:
            self.logger.error("Не удалось получить вакансии через API")
        return vacancies

    def _get_public_api_vacancies(self, search_query: str, per_page: int) -> List[Dict[str, Any]]:
        """
        Получение вакансий через публичный API.

        Args:
            search_query: Текст поискового запроса.
            per_page: Количество вакансий на странице.

        Returns:
            Список словарей с информацией о вакансиях.
        """
        self.logger.debug(
            f"Получение вакансий через публичный API. " f"Запрос: {search_query}, кол-во на странице: {per_page}"
        )

        params: Dict[str, Union[str, int]] = {"text": search_query, "per_page": per_page}

        try:
            response = self._requests.get("https://api.hh.ru/vacancies", headers=self._headers, params=params)
            response.raise_for_status()
            vacancies: List[Dict[str, Any]] = response.json().get("items", [])
            self.logger.info(f"Получено вакансий через публичный API: {len(vacancies)}")
            return vacancies
        except self._requests.RequestException as e:
            self.logger.error(f"Ошибка при получении вакансий через публичный API: {e}")
            return []
