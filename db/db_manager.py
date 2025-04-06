import psycopg2
import logging
from utils.config import config
from logger.logger import setup_logger


class DBManager:
    """
    Класс для управления базой данных PostgreSQL.
    """

    def __init__(self, database_name: str):
        """
        Инициализирует экземпляр класса DBManager.

        Args:
            database_name: Название базы данных.
        """
        self.database_name = database_name
        self.params = config()
        self.logger = setup_logger(__name__)

    def _get_connection(self):
        """
        Создает подключение к базе данных.
        """
        try:
            conn = psycopg2.connect(
                dbname=self.database_name,
                user=self.params.get('user'),
                password=self.params.get('password'),
                host=self.params.get('host'),
                port=self.params.get('port')
            )
            return conn
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(f"Ошибка при подключении к базе данных: {error}")
            return None

    def get_companies_and_vacancies_count(self) -> list[tuple[str, int]] | None:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Returns:
            Список кортежей, где первый элемент - название компании, второй - количество вакансий.
        """
        conn = self._get_connection()
        if conn is None:
            return None

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT company_name, COUNT(vacancy_id)
                FROM companies
                JOIN vacancies ON companies.company_id = vacancies.company_id
                GROUP BY company_name
                ORDER BY company_name;
            """)
            result = cur.fetchall()
            cur.close()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(f"Ошибка в get_companies_and_vacancies_count: {error}")
            return None
        finally:
            if conn is not None:
                conn.close()

    def get_all_vacancies(self) -> list[tuple[str, str, int | None, int | None, str]] | None:
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии, зарплаты и ссылки на вакансию.

        Returns:
            Список кортежей с информацией о вакансиях.
        """
        conn = self._get_connection()
        if conn is None:
            return None

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT company_name, vacancy_name, salary_from, salary_to, vacancy_url
                FROM companies
                JOIN vacancies ON companies.company_id = vacancies.company_id
                ORDER BY company_name, vacancy_name;
            """)
            result = cur.fetchall()
            cur.close()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(f"Ошибка в get_all_vacancies: {error}")
            return None
        finally:
            if conn is not None:
                conn.close()

    def get_avg_salary(self) -> float | None:
        """
        Получает среднюю зарплату по вакансиям.

        Returns:
            Средняя зарплата.
        """
        conn = self._get_connection()
        if conn is None:
            return None

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT AVG((salary_from + salary_to) / 2)
                FROM vacancies
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL;
            """)
            result = cur.fetchone()[0]
            cur.close()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(f"Ошибка в get_avg_salary: {error}")
            return None
        finally:
            if conn is not None:
                conn.close()

    def get_vacancies_with_higher_salary(self) -> list[tuple[str, str, int | None, int | None, str]] | None:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Returns:
            Список кортежей с информацией о вакансиях.
        """
        conn = self._get_connection()
        if conn is None:
            return None

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT company_name, vacancy_name, salary_from, salary_to, vacancy_url
                FROM companies
                JOIN vacancies ON companies.company_id = vacancies.company_id
                WHERE (salary_from + salary_to) / 2 > (SELECT AVG((salary_from + salary_to) / 2) FROM vacancies WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL)
                AND salary_from IS NOT NULL AND salary_to IS NOT NULL
                ORDER BY company_name, vacancy_name;
            """)
            result = cur.fetchall()
            cur.close()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(f"Ошибка в get_vacancies_with_higher_salary: {error}")
            return None
        finally:
            if conn is not None:
                conn.close()

    def get_vacancies_with_keyword(self, keyword: str) -> list[tuple[str, str, int | None, int | None, str]] | None:
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова.

        Args:
            keyword: Слово для поиска в названии вакансии.

        Returns:
            Список кортежей с информацией о вакансиях.
        """
        conn = self._get_connection()
        if conn is None:
            return None

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT company_name, vacancy_name, salary_from, salary_to, vacancy_url
                FROM companies
                JOIN vacancies ON companies.company_id = vacancies.company_id
                WHERE vacancy_name ILIKE %s
                ORDER BY company_name, vacancy_name;
            """, ('%' + keyword + '%',))
            result = cur.fetchall()
            cur.close()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(f"Ошибка в get_vacancies_with_keyword: {error}")
            return None
        finally:
            if conn is not None:
                conn.close()
