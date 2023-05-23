from jdatetime import datetime as jdt
from datetime import datetime
import asyncio
import aiohttp
import pandas as pd
import requests
import io

import codal_tsetmc.config as db
from codal_tsetmc.models import Stocks
from codal_tsetmc.tools import *
from codal_tsetmc.download.tsetmc.stock import is_stock_in_bourse_or_fara_or_paye


def get_stock_capital_daily(code: str, date = None):
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    data = "Instrument/GetInstrumentHistory"
    dict_data = get_data_from_cdn_tsetmec_api(data, code, date)
    return dict_data["instrumentHistory"]["zTitad"]


def cleanup_stock_capitals_records(response):
    df = pd.read_html(io.StringIO(response))[0]
    df.columns = ["date", "new", "old"]
    df["date"] = df["date"].jalali.parse_jalali("%Y/%m/%d").apply(lambda x: x.strftime('%Y%m%d000000'))
    df = df.sort_index(ascending=False)
    df["old"] = df["old"].apply(value_to_float)
    df["new"] = df["new"].apply(value_to_float)
    df = df[
        (df.new > df.new.shift(fill_value=0)) &
        (df.old > df.old.shift(fill_value=0))
    ]
    df = df[
        (df.old == df.new.shift(fill_value=0)) |
        (df.old == min(df.old)) |
        (df.new == max(df.new))
    ]

    df = df.sort_values("date")

    return df

def get_stock_capitals_history(code: str) -> pd.DataFrame:
    url = f"http://old.tsetmc.com/Loader.aspx?ParTree=15131H&i={code}"
    response = requests.get(url).text
    df = cleanup_stock_capitals_records(response)
    df["code"] = code

    return df

async def update_stock_capitals(code: str):
    
    try:
        if not is_stock_in_bourse_or_fara_or_paye(code):
            return
        
        jnow = jdt.now().strftime("%Y%m%d000000")
        try:
            max_date_query = (
                f"select max(up_date) as up_date from stock_capital where code = '{code}'"
            )
            max_date = pd.read_sql(max_date_query, db.engine)
            last_up_date = max_date.up_date.iat[0]

        except Exception as e:
            last_up_date = None
        try:
            # need to updata new capital data
            if last_up_date is None or last_up_date < jnow:
                url = f"http://old.tsetmc.com/Loader.aspx?ParTree=15131H&i={code}"
            else:  # The capital data for this code is updateed
                return
        except Exception as e:
            print(f"Error on formating capital:{str(e)}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        
        df = cleanup_stock_capitals_records(response)

        df["code"] = code
        df["up_date"]= jnow

        fill_table_of_db_with_df(
            df,
            columns="date",
            table="stock_capital",
            conditions=f"where code = '{code}'",
            text=f"stock: {code}"
        )

        return True, code

    except Exception as e:
        return e, code


def update_stocks_capitals(codes, msg=""):
    loop = asyncio.get_event_loop()
    tasks = [update_stock_capitals(code) for code in codes]
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


def update_stocks_group_capitals(group_code):
    stocks = db.session.query(Stocks.code).filter_by(group_code=group_code).all()
    print(f"{' '*25} group: {group_code}", end="\r")
    codes = [stock[0] for stock in stocks]
    msg = "group "+group_code+" updated"
    results = update_stocks_capitals(codes, msg)
    return results


def fill_stocks_capitals_table():
    codes = db.session.query(db.distinct(Stocks.group_code)).all()
    for i, code in enumerate(codes):
        print(
            f"{' '*35} total progress: {100*(i+1)/len(codes):.2f}%",
            end="\r",
        )
        update_stocks_group_capitals(code[0])

    print("Capital Download Finished.", " "*50)
