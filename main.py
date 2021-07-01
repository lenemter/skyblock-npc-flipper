import requests
import json
import csv
from sys import exit
import os
from time import sleep
import datetime
from tabulate import tabulate


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def get_bazaar_data(api_key: str) -> dict:
    print('Getting prices...')
    try:
        bazaar_url = f'https://api.hypixel.net/skyblock/bazaar?key={api_key}'
        request = requests.get(bazaar_url)
        if request.status_code != 200:
            raise requests.RequestException

    except requests.RequestException:
        print('Something went wrong when getting prices.')
        exit()
    except KeyboardInterrupt:
        exit()

    bazaar_data = json.loads(request.text)
    return bazaar_data


def import_items():
    try:
        items_file = open('items.csv', 'r')
        csv_reader = csv.reader(items_file)
        header = next(csv_reader)
        items = [row for row in csv_reader]
        items_file.close()
    except Exception:
        print("Can't read items.csv")
        exit()
    else:
        return items


try:
    api_key_file = open('api_key.txt', 'r')
    api_key = api_key_file.read()
    api_key_file.close()
except Exception:
    print("Can't read api_key.txt")
    exit()


def calculate() -> list:
    bazaar_data = get_bazaar_data(api_key)
    bazaar_products = bazaar_data['products']
    items = import_items()

    success = []
    for item in items:
        item_name, npc_price, item_id, enchanted_name, enchanted_id = item
        if not npc_price:
            continue
        npc_price = float(npc_price)
        product_price = round(bazaar_products[item_id]['quick_status']['sellPrice'], 1)
        product_profit = product_price * 640 - npc_price * 640
        result = [item_name, product_profit]

        # enchanted form is optional
        try:
            enchanted_price = round(bazaar_products[enchanted_id]['quick_status']['sellPrice'], 1)
            enchanted_profit = enchanted_price * 4 - npc_price * 640
            result.extend([enchanted_name, enchanted_profit])
        except Exception:
            pass
        has_enchanted = len(result) == 4
        validation = any([int(result[1]) > 0, int(result[3]) > 0]) if has_enchanted else int(result[1]) > 0
        if validation:
            success.append(result)

    return success


try:
    while True:
        clear()
        result = calculate()
        current_time = datetime.datetime.now().replace(microsecond=0)
        print(f'Last update: {current_time}')
        if result:
            header = ["Item name", "Profit", "Enchanted item name", "Enchanted profit"]
            table = tabulate(result, headers=header, tablefmt='psql', floatfmt=".1f")
            print(table)
        else:
            print('No results')
        print('Table updates automatically every 30 seconds')
        print('Press Ctrl+C to exit')
        sleep(30)
except KeyboardInterrupt:
    exit()
