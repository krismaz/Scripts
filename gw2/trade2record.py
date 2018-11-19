import gw2api.v2 as api
import gw2api as apiv1
import json
from requests import HTTPError


#Kris, seriously, fix this shit
buys, sells, current_sells, historical_buys, historical_sells, excludes = [], [], [], [], [], []
totals, adjustments = dict(), dict()


def GoldFormat(coin):
    if coin > 0:
        sign = '+'
    else:
        sign = '-'
    coin = abs(coin)
    return '{} {}g {}s {}c'.format(sign, coin//10000, (coin % 10000) // 100, coin % 100)


def Load():
    global historical_buys, historical_sells, excludes, adjustments
    with open('data/api-key.txt') as keyfile:
        key = keyfile.readline().strip()

    api.account.set_token(key)

    with open('data/historical-data.json') as historyfile:
        history = json.load(historyfile)
        historical_buys += history['buys']
        historical_sells += history['sells']

    with open('data/excludes.json') as excludesfile:
        excludes += json.load(excludesfile)

    with open('data/adjustments.json') as adjustmentsfile:
        adjustments.update(json.load(adjustmentsfile))


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

    seen_buys = set(buy['id'] for buy in buys)
    seen_sells = set(sell['id'] for sell in sells)
    buys += [buy for buy in historical_buys if buy['id'] not in seen_buys]
    sells += [sell for sell in historical_sells if sell['id'] not in seen_sells]

    with open('data/historical-data.json', 'w') as historyfile:
        json.dump({
            'buys': buys,
            'sells': sells
        }, historyfile)


def Generate():
    global sells, buys, current_sells, excludes, totals

    apiv1.set_cache_dir('./data/cache/')

    valid_items = set(sell['item_id'] for sell in sells).union(
        set(sell['item_id'] for sell in current_sells)).intersection(buy['item_id'] for buy in buys).difference(set(excludes))
    totals.update({item_id: 0 for item_id in valid_items})
    for buy in buys:
        if buy['item_id'] in valid_items:
            totals[buy['item_id']] -= buy['quantity'] * buy['price']
    for sell in sells:
        if sell['item_id'] in valid_items:
            totals[sell['item_id']] += sell['quantity'] * sell['price']*85//100



def Output():
    global totals
    format_string = "{} ({}) => {}"

    for k, v in sorted(totals.items(), key=lambda i: (i[1], i[0])):
        item = apiv1.item_details(k)

        print(format_string.format(item['name'], k, GoldFormat(v)))

    print('================================')
    print(GoldFormat(sum(totals.values())))

def Adjust():
    global totals, adjustments
    for k, v in adjustments.items():
        totals[int(k)] += v


def main():
    Load()
    Fetch()
    Generate()
    Adjust()
    Output()


if __name__ == '__main__':
    main()
