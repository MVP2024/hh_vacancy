import logging
import psycopg2
from logger.logger import setup_logger
from api.hh_data import HeadHunterData
from db.db_manager import DBManager
from utils.config import config
from db.database_manager import DatabaseManager
from db.db_creator import create_database


def fill_tables(db_name: str, params: dict, hh_data: HeadHunterData):
    """Заполняет таблицы companies и vacancies данными."""
    logger = setup_logger(__name__)
    conn = None
    try:
        conn = psycopg2.connect(dbname=db_name, **params)
        cur = conn.cursor()

        # Список компаний для заполнения (минимум 10)
        companies_data = [
            ("Яндекс", "1740"),
            ("Сбербанк", "3529"),
            ("VK", "1455"),
            ("Ozon", "23401"),
            ("Т-Банк", "78638"),
            ("Альфа-Банк", "80"),
            ("Лаборатория Касперского", "1286"),
            ("Mail.ru Group", "2177"),
            ("Avito", "1573"),
            ("Газпром", "1794"),
        ]

        # Заполняем таблицу companies и сразу получаем company_id
        companies_dict = {}
        for company_name, hh_company_id in companies_data:
            cur.execute(
                """
                INSERT INTO companies (company_name) 
                VALUES (%s) 
                ON CONFLICT (company_name) DO NOTHING
                RETURNING company_id
                """,
                (company_name,)
            )
            result = cur.fetchone()
            if result:
                companies_dict[company_name] = result[0]  # Store the company_id

        conn.commit()
        logger.info("Таблица 'companies' успешно заполнена.")

        # Заполняем таблицу vacancies через API
        for company_name, hh_company_id in companies_data:
            vacancies = hh_data.get_vacancies(hh_company_id)
            company_id = companies_dict[company_name]
            for vacancy in vacancies:
                salary_from = vacancy.get("salary", {}).get("from") if vacancy.get("salary") else None
                salary_to = vacancy.get("salary", {}).get("to") if vacancy.get("salary") else None
                vacancy_url = vacancy.get("alternate_url")
                vacancy_name = vacancy.get("name")

                cur.execute(
                    """
                    INSERT INTO vacancies (company_id, vacancy_name, salary_from, salary_to, vacancy_url)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (company_id, vacancy_name, salary_from, salary_to, vacancy_url)
                )

        conn.commit()
        logger.info("Таблица 'vacancies' успешно заполнена.")

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Ошибка при заполнении таблиц: {error}")
    finally:
        if conn is not None:
            conn.close()


def user_interaction(db_manager: DBManager):
    """Функция взаимодействия с пользователем."""
    logger = setup_logger(__name__)
    while True:
        print("\nВыберите действие:")
        print("1 - Получить список компаний и количество вакансий")
        print("2 - Получить список всех вакансий")
        print("3 - Получить среднюю зарплату по вакансиям")
        print("4 - Получить список вакансий с зарплатой выше средней")
        print("5 - Получить список вакансий по ключевому слову")
        print("0 - Выход")

        choice = input("Ваш выбор: ")

        if choice == "1":
            companies_vacancies = db_manager.get_companies_and_vacancies_count()
            if companies_vacancies:
                for company, count in companies_vacancies:
                    print(f"{company}: {count} вакансий")
            else:
                print("Не удалось получить данные о компаниях и вакансиях.")
                logger.warning("Не удалось получить данные о компаниях и вакансиях.")

        elif choice == "2":
            all_vacancies = db_manager.get_all_vacancies()
            if all_vacancies:
                for company, vacancy, salary_from, salary_to, url in all_vacancies:
                    print(f"Компания: {company}, Вакансия: {vacancy}, Зарплата: {salary_from}-{salary_to}, URL: {url}")
            else:
                print("Не удалось получить данные о вакансиях.")
                logger.warning("Не удалось получить данные о вакансиях.")

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            if avg_salary:
                print(f"Средняя зарплата: {avg_salary}")
            else:
                print("Не удалось получить среднюю зарплату.")
                logger.warning("Не удалось получить среднюю зарплату.")

        elif choice == "4":
            higher_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
            if higher_salary_vacancies:
                for company, vacancy, salary_from, salary_to, url in higher_salary_vacancies:
                    print(f"Компания: {company}, Вакансия: {vacancy}, Зарплата: {salary_from}-{salary_to}, URL: {url}")
            else:
                print("Не удалось получить данные о вакансиях с зарплатой выше средней.")
                logger.warning("Не удалось получить данные о вакансиях с зарплатой выше средней.")

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ")
            keyword_vacancies = db_manager.get_vacancies_with_keyword(keyword)
            if keyword_vacancies:
                for company, vacancy, salary_from, salary_to, url in keyword_vacancies:
                    print(f"Компания: {company}, Вакансия: {vacancy}, Зарплата: {salary_from}-{salary_to}, URL: {url}")
            else:
                print("Не удалось получить данные о вакансиях по ключевому слову.")
                logger.warning("Не удалось получить данные о вакансиях по ключевому слову.")

        elif choice == "0":
            print("Выход из программы.")
            break

        else:
            print("Некорректный выбор. Попробуйте еще раз.")
            logger.warning("Некорректный выбор.")


def main():
    """Основная функция программы."""
    logger = setup_logger("main")
    logger.info("Запуск программы.")  # Пример логирования

    db_config = config()
    db_name = db_config["database"]

    # Remove the 'database' key from db_config, as it's used separately
    db_params = db_config.copy()
    del db_params["database"]

    # Создаем базу данных
    create_database(db_name, db_params)

    # Создаем экземпляр DatabaseManager и создаем таблицы
    database_manager = DatabaseManager(db_name)
    database_manager.create_tables()

    db_manager = DBManager(db_name)

    # API configuration
    hh_data = HeadHunterData()

    # Заполняем таблицы данными
    fill_tables(db_name, db_params, hh_data)

    # Запускаем взаимодействие с пользователем
    user_interaction(db_manager)
    logger.info("Завершение программы.")  # Пример логирования


if __name__ == "__main__":
    main()