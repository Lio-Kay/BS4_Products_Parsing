import requests
import json
import time
import re
import logging

from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent


def main() -> None:
    """
    Создаем логер, хедер, получаем главную страницу через
    gather_main_page_data на её основе парсим категории продуктов через
    gather_each_page_data
    """

    # Настраиваем логгер
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s',
                        filename='logs.txt', filemode='w', encoding='utf-8')
    logging.debug('Запустили скрипт')

    # Сайт Мой здоровый рацион, страница таблиц калорийности
    url = ('https://health-diet.ru/'
           'table_calorie/?utm_source=leftMenu&utm_medium=table_calorie')
    # Создаем случайный user agent
    ua = UserAgent().firefox
    headers = {'User-Agent': ua}

    data = gather_main_page_data(headers, url)
    start_main = time.perf_counter()

    for counter, (category, category_url) in enumerate(data.items(), start=1):
        gather_each_page_data(counter, category, category_url, headers)

    emd_main = time.perf_counter()
    logging.debug(f'Закончили собирать данные')
    print(f'Закончили парсинг за {emd_main-start_main:.2f} сек,'
          f' данные сохранены в папке data, логи в logs.txt')


def gather_main_page_data(headers: dict, url: str,
                          retry: int = 3, sleep_time: int = 10) -> dict:
    """
    :param headers: user_agent из моего браузера
    :param url: url страницы таблиц калорийности из main
    :param retry: Кол-во попыток для подключения при возникновении ошибки
    :param sleep_time: Время ожидания при возникновении ошибки
    :return: Словарь с категориями продуктов и ссылками на них
    """

    start = time.perf_counter()
    # Проверка на доступность сайта
    try:
        raw_data = requests.get(url=url, headers=headers)
        logging.debug(f'Успешно получили данные с сайта через get запрос')
    except Exception as ex:
        if retry:
            logging.error(f'Попытка:{retry}, статус: '
                          f'{requests.get(url=url, headers=headers).status_code}')
            # Если все плохо - приостанавливаем код
            time.sleep(sleep_time)
            # Возвращаем функцию, уменьшив кол-во попыток,
            # и увеличив время ожидания
            return (gather_main_page_data
                    (headers, url, retry=(retry - 1), sleep_time=(sleep_time+30)))
        else:
            raise ex

    data = raw_data.text
    soup = BS(markup=data, features='lxml')

    # Получаем ссылки на все категории продуктов
    food_type_hrefs = soup.find_all('a', 'mzr-tc-group-item-href')

    # Записываем в словарь
    all_categories_dict = {}
    for row in food_type_hrefs:
        # Получаем названия категорий
        item_text = row.text
        # Создаем ссылки
        item_link = "https://health-diet.ru" + row.get('href')
        all_categories_dict.update({item_text: item_link})

    # Создаем на его основе .json, для наглядности
    with open(file='all_categories_dict.json', mode='w',
              encoding='utf-8') as file:
        json.dump(obj=all_categories_dict, fp=file,
                  indent=4, ensure_ascii=False)

    end = time.perf_counter()
    print(f'Собрали данные главной страницы и добавили ссылки на'
          f' категории в файл all_categories_dict.json за {end-start:.2f} сек.')

    return all_categories_dict


def gather_each_page_data(counter: int, category: str,
                          category_url: str, headers: dict) -> None:
    """
    :param counter: Счетчик № категории
    :param category: Категория продукта
    :param category_url: Ссылка на страницу категории
    :param headers: Информация о UserAgent
    """

    logging.debug(f'Собираем данные из категории №{counter}: {category}')
    # Боже, храни регулярки
    category_fixed = re.sub(pattern="[\s',-]", repl='_', string=category)
    product_data = requests.get(url=category_url, headers=headers).text
    soup = BS(product_data, 'lxml')
    # Если страница не доступна, пропускаем и делаем лог
    try:
        # Получаем заголовки: Продукт, Калорийность, Белки, Жиры, Углеводы
        product_headers = soup \
            .find(name='table', attrs='uk-table mzr-tc-group-table uk-table-hover uk-table-striped uk-table-condensed') \
            .find(name='tr').find_all(name='th')
        header_product = product_headers[0].text
        header_energy_value = product_headers[1].text
        header_proteins = product_headers[2].text
        header_fats = product_headers[3].text
        header_carbohydrates = product_headers[4].text

        # Записываем в csv
        with open(file=f'data/{counter}.{category_fixed}.csv', mode='w',
                  encoding='utf-8') as file:
            file.write(f'{header_product},{header_energy_value},'
                       f'{header_proteins},{header_fats},{header_carbohydrates}\n')

        # Парсим данные по продуктам
        product_table = (soup.find(class_='mzr-tc-group-table')
                         .find('tbody').find_all('tr'))
        for item in product_table:
            product_tds = item.find_all("td")
            title = product_tds[0].find("a").text
            title = title.replace(',', '.')
            calories = product_tds[1].text
            proteins = product_tds[2].text
            proteins = proteins.replace(',', '.')
            fats = product_tds[3].text
            fats = fats.replace(',', '.')
            carbohydrates = product_tds[4].text
            carbohydrates = carbohydrates.replace(',', '.')

            # Добавляем к csv в котором есть заголовки
            with open(file=f'data/{counter}.{category_fixed}.csv', mode='a',
                      encoding='utf-8') as file:
                file.write(f'{title},{calories},{proteins},'
                           f'{fats},{carbohydrates}\n')

        logging.debug(f'Закончили собирать данные из категории №{counter}:'
                      f' {category}')
    # Если отсутствует одна из страниц с данными, логируем и пропускаем её
    except AttributeError as exc:
        logging.error(f'Ошибка AttributeError {exc} в категории №{counter}:'
                      f' {category}')
        pass


if __name__ == '__main__':
    main()
