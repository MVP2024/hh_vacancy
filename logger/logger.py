import logging
import os


def setup_logger(module_name: str, log_files: str = "log_files") -> logging.Logger:
    """Настраивает логгер для указанного модуля.

    Args:
        module_name (str): Имя модуля, для которого настраивается логгер.
        log_files (str): Имя директории для хранения файлов логов. По умолчанию 'log_files'.

    Returns:
        logging.Logger: Настроенный логгер для указанного модуля.

    Эта функция создает директорию для логов, если она не существует,
    настраивает обработчик для записи логов в файл и конфигурирует формат логирования.
    """
    # Определяем абсолютный путь к директории, где находится logger.py
    logger_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(logger_dir, log_files)

    # Создаем папку logs, если она не существует
    os.makedirs(logs_dir, exist_ok=True)

    # Настраиваем формат логирования
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Создаем логгер
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)  # Уровень логирования

    # Создаем обработчик для записи логов в файл с указанием кодировки и режима 'w'
    log_file_path = os.path.join(logs_dir, f"{module_name}.log")
    file_handler = logging.FileHandler(log_file_path, mode="w", encoding="utf-8")  # Указываем кодировку и режим
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)

    return logger
