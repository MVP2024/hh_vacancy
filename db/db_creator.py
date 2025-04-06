import psycopg2
import logging
from logger.logger import setup_logger


def create_database(db_name: str, params: dict):
    """Создает базу данных, если она не существует."""
    logger = setup_logger(__name__)
    conn = None
    try:
        # Connect to the default database (postgres) to create a new one
        conn = psycopg2.connect(dbname='postgres', **params)
        conn.autocommit = True  # Necessary for creating databases
        cur = conn.cursor()

        # Check if the database exists
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        exists = cur.fetchone()

        if not exists:
            cur.execute(f"CREATE DATABASE {db_name}")
            logger.info(f"База данных '{db_name}' успешно создана.")
        else:
            logger.info(f"База данных '{db_name}' уже существует.")

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Ошибка при создании базы данных: {error}")
    finally:
        if conn is not None:
            conn.close()
