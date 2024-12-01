import json
import logging
import os
import time
from datetime import datetime
from typing import List, Optional, Tuple

import httpx
import pytz
from dotenv import load_dotenv

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

load_dotenv(verbose=True)

URL = "https://www.sj-fl.com/tools/admin_submit.ashx?action=express_query"


def extract_date(timestamp_str: str) -> str:
    """
    Преобразует строку временной метки в читаемый формат даты.

    :param timestamp_str: Строка с временной меткой в формате "/Date(1732464000000)/"
    :return: Дата в формате 'YYYY-MM-DD'
    """
    timestamp = int(timestamp_str.strip("/Date()")) // 1000
    return (
        datetime.fromtimestamp(timestamp, tz=pytz.utc)
        .astimezone(tz=pytz.timezone(os.getenv("TIMEZONE")))
        .strftime("%Y-%m-%d")
    )


def fetch_tracking_data(track_id: str) -> Optional[dict]:
    """
    Делает запрос к серверу для получения данных о трекинге.

    :param track_id: Номер отслеживания
    :return: Данные ответа в виде словаря или None в случае ошибки
    """
    data = {
        "language_id": "ru",
        "expressno": track_id,
    }
    try:
        response = httpx.post(URL, data=data, timeout=10.0)
        response.raise_for_status()
        return json.loads(response.text)
    except httpx.RequestError as e:
        logger.error(f"Ошибка запроса: {e}")
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")

    return None


def parse_events(data: dict) -> List[Tuple[str, str]]:
    """
    Извлекает список событий из данных о трекинге.

    :param data: Данные ответа сервера
    :return: Список кортежей (дата события, текст события)
    """
    events = []
    detail_list = data.get("msg", {}).get("DetailList", [])
    for item in detail_list:
        event_date = extract_date(item["ArrivalTime"])
        event_text = item["RU_Content"]
        events.append((event_date, event_text))
    return events


def send_telegram_message(message: str) -> None:
    """
    Отправляет сообщение в Telegram.

    :param message: Текст сообщения для отправки
    """
    telegram_url = (
        f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    )
    data = {
        "chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "text": message,
    }
    try:
        response = httpx.post(telegram_url, data=data)
        response.raise_for_status()
        logger.info("Сообщение успешно отправлено в Telegram")
    except httpx.RequestError as e:
        logger.error(f"Ошибка при отправке сообщения в Telegram: {e}")


def log_new_events(new_events: List[Tuple[str, str]]) -> None:
    """
    Выводит на экран новые события и отправляет их в Telegram, сортируя по дате.

    :param new_events: Список новых событий
    """
    new_events_sorted = sorted(new_events, key=lambda x: x[0])

    for event_date, event_text in new_events_sorted:
        message = f"{event_date} - {event_text}"
        logger.info(message)
        send_telegram_message(message)
        time.sleep(0.5)


def track_updates(track_id: str) -> None:
    """
    Основной цикл для отслеживания обновлений данных трекинга.

    :param track_id: Номер отслеживания
    """
    previous_events = set()

    while True:
        data = fetch_tracking_data(track_id)
        if data is None:
            logger.warning(
                "Не удалось получить данные. Повторная попытка через минуту..."
            )
            time.sleep(int(os.getenv("TIME_SLEEP")))
            continue

        current_events = parse_events(data)
        current_events_set = set(current_events)

        new_events = current_events_set - previous_events

        if new_events:
            log_new_events(list(new_events))

        previous_events = current_events_set

        time.sleep(int(os.getenv("TIME_SLEEP")))


if __name__ == "__main__":
    track_updates(track_id=os.getenv("TRACK_ID"))
