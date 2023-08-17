import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (BASE_DIR, DT_FORMAT, FILE_OUTPUT, LOG_DIR_NAME,
                       LOG_FILE_NAME, LOG_FORMAT, PRETTY_OUTPUT)


def configure_argument_parser(available_modes) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument('mode',
                        choices=available_modes,
                        help='Режимы работы парсера')
    parser.add_argument('-c',
                        '--clear-cache',
                        action='store_true',
                        help='Очистка кеша')
    parser.add_argument('-o',
                        '--output',
                        choices=(PRETTY_OUTPUT, FILE_OUTPUT),
                        help='Дополнительные способы вывода данных')

    return parser


def configure_logging() -> None:
    log_dir = BASE_DIR / LOG_DIR_NAME
    log_file = log_dir / LOG_FILE_NAME

    rotating_handler = RotatingFileHandler(log_file,
                                           maxBytes=10 ** 6,
                                           backupCount=5,
                                           encoding='utf-8')

    logging.basicConfig(datefmt=DT_FORMAT,
                        format=LOG_FORMAT,
                        level=logging.INFO,
                        handlers=(rotating_handler, logging.StreamHandler()))
