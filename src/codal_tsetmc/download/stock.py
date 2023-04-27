import requests
import re
import codal_tsetmc.config as db
from codal_tsetmc.models import Stocks


def get_stock_detail(stock_id: str, timeout = 3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }
    url = f"http://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{stock_id}"
    r = requests.get(url, headers=headers, verify=False, timeout=timeout)
    return r.json()

def create_or_update_stock_from_dict(stock_id, stock):
    print(f"creating stock with code {stock_id}")
    db.session.add(Stocks(**stock))

def update_stock_table(stock_id: str) -> Stocks:
    if exist := Stocks.query.filter_by(code=stock_id).first():
        print(f"stock with code {stock_id} exist")
    
    try:
        db.session.commit()
    except:
        print(f"stock {stock_id} exist", end="\r", flush=True)
        db.session.rollback()

    else:
        data = get_stock_detail(stock_id)

        stock = {
            "symbol": data["instrumentInfo"]["lVal18AFC"],
            "name": data["instrumentInfo"]["lVal30"],
            "isin": data["instrumentInfo"]["cIsin"],
            "code": stock_id,
            "instrument_code": data["instrumentInfo"]["insCode"],
            "instrument_id": data["instrumentInfo"]["instrumentID"],
            "group_name": data["instrumentInfo"]["sector"]["lSecVal"],
            "group_code": int(data["instrumentInfo"]["sector"]["cSecVal"].replace(" ", "")),
            "group_type": data["instrumentInfo"]["cgrValCot"],
            "market_name": data["instrumentInfo"]["flowTitle"],
            "market_code": data["instrumentInfo"]["flow"],
            "market_type": data["instrumentInfo"]["cgrValCotTitle"]
        }

        create_or_update_stock_from_dict(stock_id, stock)
    return stock

def get_stock_ids(timeout = 3):
    url = "http://tsetmc.com/tsev2/data/MarketWatchPlus.aspx?"
    r = requests.get(url, timeout=timeout)
    ids = set(re.findall(r"\d{15,20}", r.text))
    return list(ids)

def get_stock_groups(timeout = 3):
    url = "http://www.tsetmc.com/Loader.aspx?ParTree=111C1213"
    r = requests.get(url, timeout=timeout)
    return re.findall(r"\d{2}", r.text)

def fill_stocks_table(timeout = 3):
    print("Downloading group ids...")
    stocks = get_stock_ids(timeout = timeout)
    for i, stock in enumerate(stocks):
        print(
            f"{' '*50} {i+1}/{len(stocks)} ({(i+1)/len(stocks)*100:.1f}% completed)",
            end="\r", flush=True
        )
        try:
            update_stock_table(stock)
        except:
            print(f"{'='*17} {stock} failed")
            pass
