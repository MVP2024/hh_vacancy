import os
from configparser import ConfigParser


def config(filename: str | None = None, section: str = "postgresql") -> dict:
    """Читает параметры подключения к базе данных из файла database.ini."""
    # создаём синтаксический анализатор
    parser = ConfigParser()

    if filename is None:
        # Получаем каталог текущего скрипта (config.py)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Переходим в корневой каталог проекта
        project_root = os.path.dirname(script_dir)
        filename = os.path.join(project_root, "database.ini")

    # считываем файл конфигурации
    parser.read(filename)

    # раздел get, по умолчанию используется postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception("Section {0} not found in the {1} file".format(section, filename))

    return db
