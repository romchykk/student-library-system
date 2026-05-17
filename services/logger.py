"""
Централізоване логування для всього застосунку.
Пише у файл library.log і в консоль одночасно.
"""
import logging
import os
import sys


def setup_logger() -> logging.Logger:
    from services.config import LOG_LEVEL, LOG_FILENAME

    logger = logging.getLogger('library')
    if logger.handlers:
        return logger  # вже налаштовано

    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    fmt = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(module)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Файловий handler
    log_path = os.path.join(os.path.dirname(__file__), '..', LOG_FILENAME)
    log_path = os.path.abspath(log_path)
    try:
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception as e:
        print(f"[WARNING] Cannot create log file: {e}", file=sys.stderr)

    # Консольний handler (тільки WARNING і вище)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARNING)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger


# Глобальний логер — імпортувати звідси
log = setup_logger()


def log_action(role: str, username: str, action: str, details: str = ''):
    """Логує дію користувача системи."""
    msg = f"[{role.upper()}:{username}] {action}"
    if details:
        msg += f" | {details}"
    log.info(msg)


def log_error(context: str, error: Exception):
    """Логує помилку з контекстом."""
    log.error(f"{context} | {type(error).__name__}: {error}", exc_info=True)
