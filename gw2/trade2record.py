import gw2api.v2 as api
import json
from requests import HTTPError

buys, sells, current_sells, historical_buys, historical_sells = [], [], [], [], []


def Load():
    global historical_buys, historical_sells
    with open('data/api-key.txt') as keyfile:
        key = keyfile.readline().strip()

    api.account.set_token(key)

    with open('data/historical-data.json') as historyfile:
        history = json.load(historyfile)
        historical_buys += history['buys']
        historical_sells += history['sells']


def Fetch():
    global buys, sells, current_sells, historical_buys, historical_sells
    page = 0
    while True:
        try:
            buffer = api.transactions.history_buys(page=page, page_size=200)
        except HTTPError as e:
            if e.response.status_code == 400:
                break
        if not buffer:
            break
        page += 1
        buys += buffer

    page = 0
    while page < 8:
        try:
            buffer = api.transactions.history_sells(page=page, page_size=200)
        except HTTPError as e:
            if e.response.status_code == 400:
                break
        if not buffer:
            break
        page += 1
        sells += buffer

    page = 0
    while page < 8:
        try:
            buffer = api.transactions.current_sells(page=page, page_size=200)
        except HTTPError as e:
            if e.response.status_code == 400:
                break
        if not buffer:
            break
        page += 1
        current_sells += buffer

    with open('data/historical-data.json', 'w') as historyfile:
        json.dump({
            'buys': buys,
            'sells': sell
        }, historyfile)


def main():
    Load()
    Fetch()


if __name__ == '__main__':
    main()
