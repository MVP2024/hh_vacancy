import psycopg2

from logger.logger import setup_logger
from utils.config import config


class DatabaseManager:
    """
    Класс для создания и управления структурой базы данных PostgreSQL.
    """

    def __init__(self, database_name: str):
        """
        Инициализирует экземпляр класса DatabaseManager.

        Args:
            database_name: Название базы данных.
        """
        self.database_name = database_name
        self.params = config()
        self.logger = setup_logger(__name__)

    def create_tables(self) -> None:
        """Создает таблицы companies и vacancies."""
        conn = None
        try:
            conn = psycopg2.connect(
                dbname=self.database_name,
                user=self.params.get("user"),
                password=self.params.get("password"),
                host=self.params.get("host"),
                port=self.params.get("port"),
            )
            cur = conn.cursor()

            # Удаляем таблицы, если они существуют
            cur.execute("DROP TABLE IF EXISTS vacancies")
            cur.execute("DROP TABLE IF EXISTS companies")

            # Создаем таблицы
            cur.execute(
                """
                CREATE TABLE companies (
                    company_id SERIAL PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL UNIQUE
                )
            """
            )

            cur.execute(
                """
                CREATE TABLE vacancies (
                    vacancy_id SERIAL PRIMARY KEY,
                    company_id INT REFERENCES companies(company_id),
                    vacancy_name VARCHAR(255) NOT NULL,
                    salary_from INT,
                    salary_to INT,
                    vacancy_url VARCHAR(255)
                )
            """
            )

            conn.commit()
            self.logger.info("Таблицы 'companies' и 'vacancies' успешно созданы.")
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            self.logger.error(f"Ошибка при создании таблиц: {error}")
        finally:
            if conn is not None:
                conn.close()
