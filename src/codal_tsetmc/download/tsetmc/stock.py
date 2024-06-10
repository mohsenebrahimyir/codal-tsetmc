import requests
import re
import aiohttp
import pandas as pd
from codal_tsetmc.config.engine import session, engine
from codal_tsetmc.tools.api import (
    get_csv_from_github,
    get_results_by_asyncio_loop
)
from codal_tsetmc.models.stocks import Stocks, StocksGroups
from codal_tsetmc.tools.database import fill_table_of_db_with_df

INDEX_CODE = "32097828799138957"


def is_stock_in_bourse_or_fara_or_paye(code):
    group_type = ["1Z", "91", "C1", "G1", "L1", "N1", "N2", "P1", "V1", "Z1"]
    return Stocks.query.filter_by(code=code).first().group_type in group_type


def is_stock_in_akhza_bond(code):
    group_type = ["I1", "I2", "I4"]
    return Stocks.query.filter_by(code=code).first().group_type in group_type


def is_stock_in_gam_bond(code):
    stock = Stocks.query.filter_by(code=code).first()
    return stock.group_type in ["N4"] and stock.group_name in ["اوراق تامين مالي"]


def extract_instrumentInfo(data):
    return {
        "symbol": data["instrumentInfo"]["lVal18AFC"],
        "name": data["instrumentInfo"]["lVal30"],
        "name_en": data["instrumentInfo"]["lVal18"],
        "isin": data["instrumentInfo"]["cIsin"],
        "code": data["instrumentInfo"]["insCode"],
        "capital": data["instrumentInfo"]["zTitad"] if data["instrumentInfo"]["insCode"] != INDEX_CODE else 1,
        "instrument_code": data["instrumentInfo"]["insCode"],
        "instrument_id": data["instrumentInfo"]["instrumentID"],
        "group_name": data["instrumentInfo"]["sector"]["lSecVal"],
        "group_code": data["instrumentInfo"]["sector"]["cSecVal"].replace(" ", ""),
        "group_type": data["instrumentInfo"]["cgrValCot"],
        "market_name": data["instrumentInfo"]["flowTitle"],
        "market_code": data["instrumentInfo"]["flow"],
        "market_type": data["instrumentInfo"]["cgrValCotTitle"],
    }


def get_stock_detail(code: str, timeout=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
                      'Safari/537.36',
    }
    url = f"http://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{code}"
    r = requests.get(url, headers=headers, timeout=timeout)# verify=False,
    return extract_instrumentInfo(r.json())


def create_or_update_stock_from_dict(stock):
    print(f"creating stock with code {stock['code']}")
    session.add(Stocks(**stock))

    try:
        session.commit()
    except Exception as e:
        print(f"stock {stock['code']} exist", end="\r", flush=True)
        print(e.__context__)
        session.rollback()


async def update_stock_table_async(code: str) -> tuple[bool, str] | tuple[Exception, str]:
    try:
        stock = Stocks.query.filter_by(code=code).first()
        try:
            if stock.code is not None:
                if stock.code == code:
                    print(f"stock with code {code} exist")
                    return True, code
        except Exception as e:
            print(e.__context__)
            pass

        url = f"http://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
                          'Safari/537.36'
        }
        async with aiohttp.ClientSession() as ses:
            async with ses.get(url, headers=headers) as resp:
                data = await resp.json()

        stock = extract_instrumentInfo(data)
        create_or_update_stock_from_dict(stock)

        return True, code

    except Exception as e:
        return e, code


def update_stocks_table(codes):
    tasks = [update_stock_table_async(code) for code in codes]
    get_results_by_asyncio_loop(tasks)


def update_stock_table(code):
    update_stocks_table([code])


def get_stock_ids(timeout=10):
    url = "http://old.tsetmc.com/tsev2/data/MarketWatchPlus.aspx?"
    r = requests.get(url, timeout=timeout)
    ids = set(re.findall(r"\d{15,20}", r.text))
    return list(ids)


def get_stocks_groups(timeout=10):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
                      'Safari/537.36',
    }
    url = f"https://cdn.tsetmc.com/api/StaticData/GetStaticData"
    r = requests.get(url, headers=headers, timeout=timeout)
    return pd.DataFrame(r.json()["staticData"])


def fill_stocks_groups_table():
    df = get_stocks_groups()

    try:
        StocksGroups.__table__.create(engine)
    except Exception as e:
        print(e.__context__, end="\r", flush=True)

    fill_table_of_db_with_df(
        df,
        table="stocks_groups",
        columns="id"
    )


def fill_stocks_table(timeout=10, repeat=10):
    print("This may take several minutes")
    index = ["32097828799138957"]
    bonds = get_csv_from_github("treasury_bill")
    update_stocks_table(index + list(bonds.code))
    for i in range(repeat):
        print(f"Downloading group ids... series: {i + 1}")
        ids = get_stock_ids(timeout=timeout)
        update_stocks_table(ids + index)
