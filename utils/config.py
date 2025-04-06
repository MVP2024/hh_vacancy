import os
import configparser

def config(filename='database.ini', section='postgresql'):
    """
    Читает настройки из файла database.ini или database.ini.example,
    если database.ini не существует.
    """
    # Создаем парсер
    parser = configparser.ConfigParser()

    # Проверяем, существует ли database.ini
    if os.path.exists(filename):
        parser.read(filename)
    else:
        # Если database.ini не существует, пытаемся прочитать database.ini.example
        example_filename = 'database.ini.example'
        if os.path.exists(example_filename):
            parser.read(example_filename)
        else:
            raise FileNotFoundError(
                f"Файл {filename} или {example_filename} не найден. "
                f"Пожалуйста, создайте файл {filename} на основе {example_filename}."
            )

    # Получаем настройки указанной секции
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Секция {section} не найдена в файле {filename}")

    return db
