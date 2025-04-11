from typing import Any, Dict, List

import requests

from logger.logger import setup_logger


class HeadHunterData:
    """
    Класс для получения данных с HeadHunter API.
    """

    def __init__(self) -> None:
        """
        Инициализирует экземпляр класса HeadHunterData.
        """
        self.logger = setup_logger(__name__)

    def get_companies(self, company_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Получает информацию о компаниях по их ID.

        Args:
            company_ids: Список ID компаний.

        Returns:
            Список словарей с информацией о компаниях.
        """
        companies: List[Dict[str, Any]] = []
        for company_id in company_ids:
            try:
                url = f"https://api.hh.ru/employers/{company_id}"
                response = requests.get(url)
                response.raise_for_status()
                companies.append(response.json())
                self.logger.info(f"Получена информация о компании {company_id}")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Ошибка при получении компании {company_id}: {e}")
        return companies

    def get_vacancies(self, company_id: str) -> List[Dict[str, Any]]:
        """
        Получает список вакансий компании по ее ID.

        Args:
            company_id: ID компании.

        Returns:
            Список словарей с информацией о вакансиях.
        """
        vacancies: List[Dict[str, Any]] = []
        try:
            url = f"https://api.hh.ru/vacancies?employer_id={company_id}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            vacancies.extend(data.get("items", []))
            self.logger.info(f"Получены вакансии компании {company_id}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ошибка при получении вакансий компании {company_id}: {e}")
        return vacancies
