"""
Читання конфігурації з config.ini.
Використовується по всьому проєкту замість захардкоджених значень.
"""
import configparser
import os

_cfg = configparser.ConfigParser()

# Шукаємо config.ini поруч із цим файлом або в корені проєкту
_cfg_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
_cfg_path = os.path.abspath(_cfg_path)

if os.path.exists(_cfg_path):
    _cfg.read(_cfg_path, encoding='utf-8')
else:
    # Значення за замовчуванням якщо файл не знайдено
    _cfg['library']  = {'max_issuances': '4', 'default_loan_days': '14',
                         'name': 'Студентська бібліотека'}
    _cfg['database'] = {'filename': 'library.db'}
    _cfg['logging']  = {'level': 'INFO', 'filename': 'library.log'}


def get(section: str, key: str, fallback=None):
    return _cfg.get(section, key, fallback=fallback)

def get_int(section: str, key: str, fallback: int = 0) -> int:
    return _cfg.getint(section, key, fallback=fallback)

# Зручні константи
MAX_ISSUANCES      = get_int('library',  'max_issuances',    4)
DEFAULT_LOAN_DAYS  = get_int('library',  'default_loan_days', 14)
LIBRARY_NAME       = get('library',      'name',             'Студентська бібліотека')
DB_FILENAME        = get('database',     'filename',         'library.db')
LOG_LEVEL          = get('logging',      'level',            'INFO')
LOG_FILENAME       = get('logging',      'filename',         'library.log')
