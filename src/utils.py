import logging
from typing import Callable

from bs4 import BeautifulSoup, Tag
from requests import RequestException
from requests_cache import CachedSession, Response

from exceptions import ParserFindTagException


def get_response(session: CachedSession, url: str) -> Response:
    try:
        response = session.get(url)
        response.encoding = 'utf-8'

        return response

    except RequestException:
        logging.exception(f'Возникла ошибка при загрузке страницы {url}',
                          stack_info=True)


def find_tag(soup: BeautifulSoup, tag: str, attrs: dict[str] = None) -> Tag:
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)

        raise ParserFindTagException(error_msg)

    return searched_tag


def find_tag_by_lambda(soup: BeautifulSoup, func: Callable) -> Tag:
    searched_tag = soup.find(func)
    if searched_tag is None:
        error_msg = 'По заданным в функции условиям тег не найден'
        logging.error(error_msg, stack_info=True)

        raise ParserFindTagException(error_msg)

    return searched_tag
