# Парсер таблиц питательных веществ на BeautifulSoup4

## Описание
Программа для сбора информации по 54 категориям различных продуктов с сайта
Мой здоровый рацион (https://health-diet.ru). Сделана на основе библиотеки
BeautifulSoup4 без использования асинхронности. Время сбора информации
примерно 30 секунд. Взаимодействие осуществляется через CLI.

## Пример получаемых данных
![usage_example_1.png](readme_assets%2Fusage_example_1.png)

## Инициализация проекта
Введите в консоль (UNIX):
  ```sh
  git clone https://github.com/Lio-Kay/BS4_Products_Parsing
  cd BS4_Products_Parsing/
  poetry shell
  poetry install
  python main.py
  ```
После завершения данные можно будет найти в папке data

## Описание структуры проекта
* data - Создается при запуске
  - Файлы формата: "Номер.Название_категории.csv" с данными о продуктах
* readme_assets - Файлы для README.md
* all_categories_dict.json - Создается при запуске. Словарь со списком ссылок на категории
* logs.txt - Создается при запуске. Логи всех действий парсера
* main.py - Основная логика

## Технологии в проекте
Библиотеки:
* requests
* beautifulsoup4
* fake_useragent
* json
* time
* re
* logging

Другие особенности:
* poetry вместо venv/pip
* Логирование запросов
