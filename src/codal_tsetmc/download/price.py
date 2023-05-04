from jdatetime import date as jdate
from jdatetime import datetime as jdt
from datetime import datetime
import asyncio
import aiohttp
import pandas as pd
import requests
import io
import json
import requests

import codal_tsetmc.config as db
from codal_tsetmc.models import StockPrice, Stocks
from codal_tsetmc.tools import (
    get_data_from_cdn_tsetmec_api,
    datetime_to_num,
    fill_table_of_db_with_df
)
from codal_tsetmc.download.stock import is_stock_in_bourse_or_fara_or_paye

def get_index_price_history():
    index = "32097828799138957"
    url = f'http://www.tsetmc.com/tsev2/chart/data/Index.aspx?i={index}&t=value'
    s = requests.get(url, verify=False).content
    df = pd.read_csv(io.StringIO(s.decode("utf-8").replace(";", "\n")), header=None)
    df.columns = ["date", "price"]
    df["date"] = df["date"].apply(lambda x: jdt.strptime(str(x), "%Y/%m/%d"))
    df["date"] = df["date"].apply(lambda x: datetime_to_num(str(x)))
    df["code"] = index
    df["ticker"] = "INDEX"

    return df


def cleanup_price_records(response):
    df = pd.read_csv(io.StringIO(response))
    df.columns = [i[1:-1].lower() for i in df.columns]
    df["date"] = df["dtyyyymmdd"].apply(lambda x: datetime.strptime(str(x), "%Y%m%d"))
    df["date"] = df["date"].jalali.to_jalali().apply(lambda x: datetime_to_num(str(x)))
    df["price"] = df["close"]

    return df[["date", "ticker", "price"]]

def get_stock_price_history(code: str, from_date="20000101", to_date=datetime.now().strftime("%Y%m%d")) -> pd.DataFrame:
    url = f"http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={code}&DateFrom={from_date}&DateTo={to_date}&b=0"
    response = requests.get(url).text
    df = cleanup_price_records(response)
    df["code"] = code

    return df

async def update_stock_price(code: str):
    try:
        if not is_stock_in_bourse_or_fara_or_paye(code):
            return
        now = datetime.now().strftime("%Y%m%d")
        jnow = int(jdt.now().strftime("%Y%m%d"))*1e6
        try:
            max_date_query = (
                f"select max(date) as date from stock_price where code = '{code}'"
            )
            max_date = pd.read_sql(max_date_query, db.engine)
            last_date = max_date.date.iat[0]
            last_update = max_date.update.iat[0]
        except Exception as e:
            last_date = None
        try:
            if last_date is None:  # no any record added in database
                url = f"http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={code}&DateFrom=20000101&DateTo={now}&b=0"
            elif last_date < jnow or last_update < jnow:  # need to updata new price data
                url = f"http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={code}&DateFrom={str(last_date)}&DateTo={now}&b=0"
            else:  # The price data for this code is updateed
                return
        except Exception as e:
            print(f"Error on formating price:{str(e)}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        
        df = cleanup_price_records(response)
        df["code"] = code
        df["update"]= jnow

        fill_table_of_db_with_df(df, "stock_price", text=f"stock {code}")

        return True, code

    except Exception as e:
        return e, code


def update_group_price(code):
    stocks = db.session.query(Stocks.code).filter_by(group_code=code).all()
    print(f"{' '*25} group {code}", end="\r")
    loop = asyncio.get_event_loop()
    tasks = [update_stock_price(stock[0]) for stock in stocks]
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
        print("from codal_tsetmc.download import get_all_price")
        print("get_all_price()")
        print("```")
        raise RuntimeError

    print("group", code, "updated", end="\r")
    return results


def get_all_price():
    codes = db.session.query(db.distinct(Stocks.group_code)).all()
    for i, code in enumerate(codes):
        print(
            f"{' '*35} total progress: {100*(i+1)/len(codes):.2f}%",
            end="\r",
        )
        update_group_price(code[0])

    print("Price Download Finished.", " "*50)


def get_number_of_shares_daily(code: str, date: str):
    data = "Instrument/GetInstrumentHistory"
    dict_data = get_data_from_cdn_tsetmec_api(data, code, date)
    return dict_data["instrumentHistory"]["zTitad"]

def get_closing_price_daily(code: str, date: str):
    data = "ClosingPrice/GetClosingPriceDaily"
    dict_data = get_data_from_cdn_tsetmec_api(data, code, date)
    
    return dict_data["closingPriceDaily"]["pClosing"]

def get_market_value(code, date):
    share = get_number_of_shares_daily(code, date)
    price = get_closing_price_daily(code, date)

    return price * share
