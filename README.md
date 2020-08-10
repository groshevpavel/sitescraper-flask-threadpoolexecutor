# timeweb
## Тестовое задание
Написать API на Flask для парсинга сайтов с двумя методами. 
- POST запрос получает адрес сайта и в ответ возвращает ID
 задачи. 
- GET запрос по ID задачи возвращает текущее состояние задачи. 
    - Когда задача выполнена, возвращает URL, по которому можно скачать архив.

В задание входит парсер, который пробегается по сайту с лимитированной вложенностью, например, до 3 уровней и сохраняет html/css/js и медиа файлы

## Решение

- Запуск задания
```bash
curl --location --request POST 'http://0.0.0.0:8080/scrape' \
--header 'Content-Type: application/json' \
--data-raw '{
    "url": "https://yandex.ru",
    "depth": 3
}'
```
пример ответа:
```json
{
  "task_id": 1
}
```

- Проверка статуса или получение результирующего архива
```bash
curl --location --request GET 'http://0.0.0.0:8080/task/1'
```
пример ответа когда задача выполняется:
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

## Подготовка к запуску
Создание виртуального окружения для запуска приложения
```bash
pip install pipenv
pipenv install
```

Запуск приложения
```bash
export FLASK_APP=app.py
python -m flask run
```