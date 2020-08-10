# Site scraper
## based on Flask & concurrent.futures.ThreadPoolExecutor
Simple Flask REST API that starts site scrape task
- POST request has site address and site scrape depth level and returns scrape task_id
- GET request returns task current state and some scrape info while task in process
    - When task completed it returns .zip file with scraped files in. Folder structure keeps on

Flask used for build REST API and concurrent.futures.ThreadPoolExecutor to start non-blocking scrape task and run
 it
 HTTP requests by requests lib, html parsing by lxml.html

## Тестовое задание
Написать API на Flask для парсинга сайтов с двумя методами. 
- POST запрос получает адрес сайта и в ответ возвращает ID
 задачи. 
- GET запрос по ID задачи возвращает текущее состояние задачи. 
    - Когда задача выполнена, возвращает URL, по которому можно скачать архив.

В задание входит парсер, который пробегается по сайту с лимитированной вложенностью, например, до 3 уровней и сохраняет html/css/js и медиа файлы

## Решение

- Запуск задания \ Task launching
```bash
curl --location --request POST 'http://0.0.0.0:8080/scrape' \
--header 'Content-Type: application/json' \
--data-raw '{
    "url": "https://yandex.ru",
    "depth": 1
}'
```
пример ответа \ response example:
```json
{
  "task_id": 1
}
```

- Проверка статуса или получение результирующего архива \ Task status checking
```bash
curl --location --request GET 'http://0.0.0.0:8080/task/1'
```
пример ответа когда задача выполняется \ response when task is running:
```json
{
  "bytes_downloaded": 589156,
  "files_processed": 3,
  "links_processed": 1395,
  "status": "CRAWLING",
  "task_id": 1
}
```
```json
{
  "bytes_downloaded": 249589059,
  "files_processed": 304,
  "links_processed": 7591,
  "status": "ZIPPING RESULTS",
  "task_id": 1
} 
```

## Подготовка к запуску \ Setup for launch
Создание виртуального окружения для запуска приложения \ Setup virtual environment for app start
```bash
pip install pipenv
pipenv install
```

Запуск приложения \ Start app
```bash
export FLASK_APP=app.py
python -m flask run
```