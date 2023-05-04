from jdatetime import datetime as jdt
import asyncio
import aiohttp
import pandas as pd
import requests
import io

import codal_tsetmc.config as db
from codal_tsetmc.models import Stocks
from codal_tsetmc.tools.string_edit import *
from codal_tsetmc.tools.database import *
from codal_tsetmc.download.stock import is_stock_in_bourse_or_fara_or_paye


def cleanup_capital_records(response):
    df = pd.read_html(io.StringIO(response))[0]
    df.columns = ["date", "new", "old"]
    df["date"] = df["date"].apply(datetime_to_num)
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

    return df

def get_stock_capital_history(code: str) -> pd.DataFrame:
    url = f"http://tsetmc.com/Loader.aspx?ParTree=15131H&i={code}"
    response = requests.get(url).text
    df = cleanup_capital_records(response)
    df["code"] = code

    return df


async def update_stock_capital(code: str):
    
    try:
        if not is_stock_in_bourse_or_fara_or_paye(code):
            return
        
        jnow = int(jdt.now().strftime("%Y%m%d"))*1e6
        try:
            max_date_query = (
                f"select max(date) as date from stock_capital where code = '{code}'"
            )
            max_date = pd.read_sql(max_date_query, db.engine)
            last_date = max_date.date.iat[0]
            last_update = max_date.update.iat[0]

        except Exception as e:
            last_date = None
        try:
            # need to updata new capital data
            if last_date is None or last_date < jnow or last_update < jnow:
                url = f"http://tsetmc.com/Loader.aspx?ParTree=15131H&i={code}"
            else:  # The capital data for this code is updateed
                return
        except Exception as e:
            print(f"Error on formating capital:{str(e)}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()
        
        df = cleanup_capital_records(response)
        df["code"] = code
        df["update"]= jnow
        
        fill_table_of_db_with_df(df, "stock_capital", text=f"stock {code}")

        return True, code

    except Exception as e:
        return e, code


def update_group_capital(code):
    stocks = db.session.query(Stocks.code).filter_by(group_code=code).all()
    print(f"{' '*25} group {code}", end="\r")
    loop = asyncio.get_event_loop()
    tasks = [update_stock_capital(stock[0]) for stock in stocks]
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
        print("from codal_tsetmc.download import get_all_capital")
        print("get_all_capital()")
        print("```")
        raise RuntimeError

    print("group", code, "updated", end="\r")
    return results


def get_all_capital():
    codes = db.session.query(db.distinct(Stocks.group_code)).all()
    for i, code in enumerate(codes):
        print(
            f"{' '*35} total progress: {100*(i+1)/len(codes):.2f}%",
            end="\r",
        )
        update_group_capital(code[0])

    print("Capital Download Finished.", " "*20)
