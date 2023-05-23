import requests
import re
import asyncio
import aiohttp
import codal_tsetmc.config as db
from codal_tsetmc.models import Stocks

def is_stock_in_bourse_or_fara_or_paye(code):
    group_type = ["1Z", "91", "C1", "G1", "L1", "N1", "N2", "P1", "V1", "Z1"]
    return Stocks.query.filter_by(code=code).first().group_type in group_type

def get_stock_detail(code: str, timeout = 3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }
    url = f"http://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{code}"
    r = requests.get(url, headers=headers, verify=False, timeout=timeout)
    return r.json()

def create_or_update_stock_from_dict(stock):
    print(f"creating stock with code {stock['code']}")
    db.session.add(Stocks(**stock))
    
    try:
        db.session.commit()
    except:
        print(f"stock {stock['code']} exist", end="\r", flush=True)
        db.session.rollback()

async def update_stock_table(code: str) -> Stocks:
    try:
        if exist := Stocks.query.filter_by(code=code).first():
            print(f"stock with code {code} exist")
            return
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        }
        url = f"http://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{code}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        stock = {
            "symbol": data["instrumentInfo"]["lVal18AFC"],
            "name": data["instrumentInfo"]["lVal30"],
            "isin": data["instrumentInfo"]["cIsin"],
            "code": code,
            "capital": data["instrumentInfo"]["zTitad"] if code != "32097828799138957" else 1_000_000_000,
            "instrument_code": data["instrumentInfo"]["insCode"],
            "instrument_id": data["instrumentInfo"]["instrumentID"],
            "group_name": data["instrumentInfo"]["sector"]["lSecVal"],
            "group_code": data["instrumentInfo"]["sector"]["cSecVal"].replace(" ", ""),
            "group_type": data["instrumentInfo"]["cgrValCot"],
            "market_name": data["instrumentInfo"]["flowTitle"],
            "market_code": data["instrumentInfo"]["flow"],
            "market_type": data["instrumentInfo"]["cgrValCotTitle"],
        }

        create_or_update_stock_from_dict(stock)

        return True, code

    except Exception as e:
        return e, code

def update_stocks_table(codes, msg=""):
    loop = asyncio.get_event_loop()
    tasks = [update_stock_table(code) for code in codes]
    try:
        results = loop.run_until_complete(asyncio.gather(*tasks))
    except RuntimeError:
        WARNING_COLOR = "\033[93m"
        ENDING_COLOR = "\033[0m"
        print(WARNING_COLOR, "Please update stock table", ENDING_COLOR)
        print(
            f"{WARNING_COLOR}If you are using jupyter notebook, please run following command:{ENDING_COLOR}"
        )
        print("```")
        print("%pip install nest_asyncio")
        print("import nest_asyncio; nest_asyncio.apply()")
        print("```")
        raise RuntimeError
    print(msg, end="\r")
    return results

def get_stock_ids(timeout = 10):
    url = "http://old.tsetmc.com/tsev2/data/MarketWatchPlus.aspx?"
    r = requests.get(url, timeout=timeout)
    ids = set(re.findall(r"\d{15,20}", r.text))
    return list(ids)

def get_stocks_groups(timeout = 10):
    url = "http://old.tsetmc.com/Loader.aspx?ParTree=111C1213"
    r = requests.get(url, timeout=timeout)
    return re.findall(r"\d{2}", r.text)

def fill_stocks_table(timeout = 10):
    i = 30
    while i > 1:
        print(f"Downloading group ids... seris: {31 - i}")
        stocks = get_stock_ids(timeout=timeout)
        stocks = ["32097828799138957"] + stocks
        update_stocks_table(stocks)
        i -= 1
