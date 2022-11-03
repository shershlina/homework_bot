import logging
import os
import sys

import requests
import time

import telegram
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='homework.log',
    filemode='a')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: dict = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES: dict = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(f'Ошибка отправки сообщения в Telegram {error}')
        raise telegram.error.BadRequest('Бот не смог отправить сообщение')
    else:
        logger.info('Отправлено сообщение в Telegram')


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API."""
    current_timestamp = current_timestamp or int(time.time())
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != 200:
        logger.error('API недоступен')
        raise requests.HTTPError(f'Response {response.status_code}')
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        logger.error('Ошибка обработки результата запроса к API')
        raise requests.exceptions.JSONDecodeError


def check_response(response):
    """Проверка корректности ответа API."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является словарём')
    if 'homeworks' not in response:
        logger.error('Не хватает ключа homeworks в словаре')
        raise IndexError('Не хватает ключа homeworks в словаре')
    if not isinstance(response['homeworks'], list):
        raise TypeError('В ответе API не содержится список домашних работ')
    return response['homeworks']


def parse_status(homework):
    """Проверка изменения статуса работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if not all([homework_name, homework_status]):
        raise KeyError('В словаре не найден нужный ключ')
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except KeyError:
        logger.error('Неопознанный статус работы')
        raise KeyError('Неопознанный статус работы')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет наличие всех нужных переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Переданы не все токены')
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    error_message = ''
    while True:
        try:
            response = check_response(get_api_answer(current_timestamp))
            if len(response) != 0:
                homework = response[0]
                message = parse_status(homework)
                send_message(bot, message)
                logger.info('Изменился статус домашней работы')
            else:
                logger.debug('Список домашних работ пуст')
        except Exception as error:
            logger.error(f'В работе возникла ошибка {error}')
            new_error = f'В работе возникла ошибка {error}'
            if new_error != error_message:
                send_message(bot, f'В работе возникла ошибка {error}')
                error_message = new_error
        finally:
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
