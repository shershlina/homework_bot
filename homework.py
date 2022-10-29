import logging
import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME: int = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщения в чат."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API."""
    params = {'from_date': current_timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
    if response.status_code != 200:
        raise OSError("Response " + str(response.status_code))
    homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return homework_statuses.json()


def check_response(response):
    """Проверка корректности ответа API."""
    try:
        response
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
    if type(response) != dict:
        raise TypeError('Ответ API не является словарём')
    if type(response['homeworks']) != list:
        raise TypeError('В ответе API не содержится список домашних работ')
    return response['homeworks']


def parse_status(homework):
    """Проверка изменения статуса работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет наличие всех нужных переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(tokens)


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 0
    homework = check_response(get_api_answer(current_timestamp))[0]
    old_status = ''
    while True:
        homework_status = homework['status']
        if old_status == homework_status:
            old_status = homework_status
            time.sleep(RETRY_TIME)
        else:
            message = parse_status(homework)
            send_message(bot, message)
            old_status = homework_status
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
