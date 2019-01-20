import logging
from logging import handlers
import os
import sys
import inspect

# Смотрит, есть ли уже каталог для логгирования, и нет ли файла с именем log.
# Если каталога нет, создает его. Если есть - пишет ошибку в консоль о невозможности создать каталог.
try:
    os.makedirs('log', exist_ok=True)
except FileExistsError:
    print('There is a file with name \'log\' already exists!')

# Инициализируем логгер с именем app.main
logger = logging.getLogger('app.main')

# Задаем требуемое форматирование
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s : %(message)s ")

# Пробуем писать лог, ротирование каждую минуту (для теста), используем заданный формат лога.
# Если сущуествует каталог с именем server.log, то выдаем в консоль ошибку о невозможности создать файл.
try:
    rot_hand = handlers.logging.handlers.TimedRotatingFileHandler(
        'log/server.log', when='D', interval=1,
        encoding='utf-8',
        backupCount=10
    )
    rot_hand.setFormatter(formatter)
    logger.addHandler(rot_hand)
except PermissionError:
    print('There is a directory with name \'server.log\' already exists in \'log\' catalogue!')
    sys.exit()

class Log:
    """
    Class of decorator, Used to log functions calls.
    """
    def __init__(self):
        pass

    # Магический метод __call__ позволяет обращаться к
    # объекту класса, как к функции
    def __call__(self, func):
        def decorated(*args, **kwargs):
            whosdaddy = inspect.stack()[1][3]
            res = func(*args, **kwargs)
            logger.debug(
                'Function {} with args {}, kwargs {} = {} was called '
                'from function {}.'.format(
                    func.__name__, args, kwargs, res, whosdaddy)
            )
            return res

        return decorated