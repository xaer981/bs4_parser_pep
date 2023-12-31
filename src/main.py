import logging
import re
from collections import defaultdict
from typing import Union
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOADS_DIR_NAME, EXPECTED_STATUS,
                       LATEST_VERSIONS_TITLES, MAIN_DOC_URL, PEP_TITLES,
                       PEP_URL, WHATS_NEW_TITLES)
from exceptions import NotFoundVersionsException
from outputs import control_output
from utils import find_tag, find_tag_by_lambda, get_response


def whats_new(session: CachedSession) -> Union[list[tuple], None]:
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:

        return None

    soup = BeautifulSoup(response.text, 'lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})

    results = [WHATS_NEW_TITLES]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:

            return None

        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')

        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session: CachedSession) -> Union[list[tuple], None]:
    response = get_response(session, MAIN_DOC_URL)
    if response is None:

        return None

    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break

    else:
        raise NotFoundVersionsException('Ничего не нашлось')

    results = [LATEST_VERSIONS_TITLES]

    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''

        results.append((link, version, status))

    return results


def download(session: CachedSession) -> None:
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)

    soup = BeautifulSoup(response.text, 'lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag,
                          'a',
                          {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS_DIR_NAME
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session: CachedSession) -> list[tuple]:
    response = get_response(session, PEP_URL)
    if response is None:

        return None

    soup = BeautifulSoup(response.text, 'lxml')
    section = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tr_tags = section.tbody.find_all('tr')

    results = defaultdict(int)

    for tr in tqdm(tr_tags, desc='Список PEP обрабатывается...'):
        pep_status, pep_href = tr.abbr.text[1:], tr.a['href']
        cur_pep_link = urljoin(PEP_URL, pep_href)
        cur_pep_response = get_response(session, cur_pep_link)
        if cur_pep_response is None:

            return None

        pep_soup = BeautifulSoup(cur_pep_response.text, 'lxml')
        dt_tag = find_tag_by_lambda(pep_soup, (lambda tag: tag.name == 'dt'
                                               and 'Status' in tag.text))
        pep_status_from_href = dt_tag.find_next_sibling('dd').text

        if pep_status_from_href not in EXPECTED_STATUS[pep_status]:
            logging.error(f'Статусы не совпадают: {cur_pep_link}\n'
                          f'Статус в карточке: {pep_status_from_href}\n'
                          f'Ожидаемые статусы: {EXPECTED_STATUS[pep_status]}')

        results[pep_status_from_href] += 1

    results['Total'] = sum(results.values())
    results = list(results.items())
    results.insert(0, PEP_TITLES)

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main() -> None:
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
