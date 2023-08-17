from pathlib import Path

BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR_NAME = 'downloads'
LOG_DIR_NAME = 'logs'
LOG_FILE_NAME = 'parser.log'
RESULTS_DIR_NAME = 'results'

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'

EXPECTED_STATUS = {
        'A': ('Active', 'Accepted'),
        'D': ('Deferred',),
        'F': ('Final',),
        'P': ('Provisional',),
        'R': ('Rejected',),
        'S': ('Superseded',),
        'W': ('Withdrawn',),
        '': ('Draft', 'Active'),
    }
FILE_OUTPUT = 'file'
PRETTY_OUTPUT = 'pretty'

LATEST_VERSIONS_TITLES = ('Ссылка на документацию', 'Версия', 'Статус')
PEP_TITLES = ('Статус', 'Количество')
WHATS_NEW_TITLES = ('Ссылка на статью', 'Заголовок', 'Редактор, Автор')

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
