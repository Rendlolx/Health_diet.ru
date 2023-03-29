import requests
import json
import csv
import random

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from time import sleep

ua = UserAgent()


headers = {
    "Accept": '*/*',
    "UserAgent": ua.random
}

url = "http://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"

response = requests.get(url, headers=headers)
src = response.text


# Записываем страницу в файл, чтобы не делать лишние запросы!
with open("index.html", "w", encoding="UTF-8") as file:
    file.write(src)

# Собираем нужные данные из страницы: 
with open("index.html", encoding="UTF-8") as file:
    src = file.read()

soup = BeautifulSoup(src, "lxml")
links = soup.find_all("a", class_="mzr-tc-group-item-href")

all_cat_dict = {}
for item in links:
    item_text = item.text
    item_link = "http://health-diet.ru" + item.get("href")

    all_cat_dict[item_text] = item_link

# Записываем в JSON, чтобы работать со страницами каждой продукции:
with open("all_cat_dict.json", "w", encoding="UTF-8") as file:
    # indent - отступ, ensure_ascii - Кодировка
    json.dump(all_cat_dict, file, indent=4, ensure_ascii=False) 

# Загружаем из JSON'а данные:
with open("all_cat_dict.json", encoding="UTF-8") as file:
    all_categories = json.load(file)

iteration_count = int(len(all_categories)) - 1
count = 0
print(f"Всего страниц: {iteration_count}")

for category_name, category_href in all_categories.items():
    response = requests.get(url=category_href, headers=headers)
    src = response.text
    
    with open(
        f"html/{count}_{category_name}.html", 
        "w", 
        encoding="UTF-8"
    ) as file:
        file.write(src)

    with open(
        f"html/{count}_{category_name}.html", encoding="UTF-8"
    ) as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # Проверка страницы на присутствие данных
    alert = soup.find(class_="uk-alert-danger")

    if alert is not None:
        continue

    #Собираем заголовки таблицы
    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    with open(
        f"csv/{count}_{category_name}.csv", 
        "w", 
        encoding="UTF-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(
            (
            product,
            calories,
            proteins,
            fats,
            carbohydrates,
            )
        )

    # Собираем данные продуктов
    products_info = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    products_json = []

    for item in products_info:
        products_tds = item.find_all("td")

        name_prod = products_tds[0].find("a").text
        calories = products_tds[1].text
        proteins = products_tds[2].text
        fats = products_tds[3].text
        carbohydrates = products_tds[4].text

        with open(
            f"csv/{count}_{category_name}.csv", 
            "a", 
            encoding="UTF-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                name_prod,
                calories,
                proteins,
                fats,
                carbohydrates,
            )
        )
            
    with open(
        f"data/{count}_{category_name}.json", 
        "a", 
        encoding="UTF-8"
    ) as file:
        json.dump(products_json, file, indent=4, ensure_ascii=False)

    count += 1
    print(f"Страница № {count}. {category_name} записан!")
    iteration_count -= 1

    if iteration_count == 0:
        print(f"Выгрузка завершена")
        break

    print(f"осталось страниц: {iteration_count}")
    sleep(random.randrange(2, 5))
