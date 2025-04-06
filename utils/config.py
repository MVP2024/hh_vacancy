import os
from configparser import ConfigParser


def config(filename=None, section="postgresql") -> dict:
    """Читает параметры подключения к базе данных из файла database.ini."""
    # create a parser
    parser = ConfigParser()

    if filename is None:
        # Get the directory of the current script (config.py)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to the project root directory
        project_root = os.path.dirname(script_dir)
        filename = os.path.join(project_root, "database.ini")

    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db