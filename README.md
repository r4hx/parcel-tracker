# parcel-tracker: Отслеживание посылок с уведомлениями в Telegram

Этот проект представляет собой скрипт для автоматического отслеживания статуса доставки посылок и отправки уведомлений о новых событиях в Telegram. Скрипт запрашивает данные о трекинге по API, обрабатывает их и отправляет обновления в указанный Telegram-чат.

## Основные функции

- **Отправка запросов к API**: Запросы к серверу для получения информации о трекинге.
- **Обработка событий**: Извлечение и форматирование событий доставки.
- **Отправка уведомлений**: Передача сообщений с обновлениями в Telegram.
- **Цикл отслеживания**: Постоянный мониторинг обновлений с заданным интервалом.

## Установка и настройка

1. **Клонирование репозитория**:
   ```bash
   git clone https://github.com/r4hx/parcel-tracker.git
   cd parcel-tracker
   ```

2. **Установка зависимостей**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Создание файла окружения** `.env`:
   ```ini
   TIMEZONE=Europe/Moscow
   TIME_SLEEP=60  # интервал опроса в секундах
   TELEGRAM_BOT_TOKEN=ваш_токен_бота
   TELEGRAM_CHAT_ID=ваш_чат_id
   TRACK_ID=ваш_номер_отслеживания
   ```

4. **Запуск скрипта**:
   ```bash
   python track.py
   ```

## Зависимости

- `httpx`
- `python-dotenv`
- `pytz`

## Контакты

Если у вас есть вопросы или предложения, создайте issue

---
