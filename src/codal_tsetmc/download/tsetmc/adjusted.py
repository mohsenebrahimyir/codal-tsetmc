from datetime import datetime
import asyncio
import aiohttp
import pandas as pd
import requests
import io

import codal_tsetmc.config as db
from codal_tsetmc.models import Stocks


def get_stock_adjusted_history(stock_id: str) -> pd.DataFrame:
    """Get stock adjusted from the web.

    params:
    ----------------
    code: int
        http://tsetmc.com/Loader.aspx?ParTree=15131G&i=46348559193224090#
        interger after i=

    return:
    ----------------
    pd.DataFrame
        dtyyyymmdd: str
        old_price = float
        new_price = float

    example
    ----------------
    df = get_stock_adjusted_history("46348559193224090")
    """
    url = f"http://tsetmc.com/Loader.aspx?ParTree=15131G&i={stock_id}"
    r = requests.get(url)
    df = pd.read_html(r.text)[0]
    df.columns = ["date", "new_price", "old_price"]
    df["date"] = df.date.jalali.parse_jalali("%Y/%m/%d")
    df["dtyyyymmdd"] = (
        df.date.jalali
        .to_gregorian()
        .apply(lambda x: x.strftime("%Y%m%d"))
        .astype(int)
    )

    return df


async def update_stock_adjusted(code: str):
    """
    Update (or download for the first time) Stock adjusted


    params:
    ----------------
    code: str or intege

    example
    ----------------
    `update_stock_adjusted('44891482026867833') #Done`
    """
    try:
        now = datetime.now().strftime("%Y%m%d")
        try:
            max_date_query = (
                f"select max(dtyyyymmdd) as date from stock_adjusted where code = '{code}'"
            )
            max_date = pd.read_sql(max_date_query, db.engine)
            last_date = max_date.date.iat[0]
        except Exception as e:
            last_date = None
        try:
            # need to updata new adjusted data
            if last_date is None or str(last_date) < now:
                url = f"http://tsetmc.com/Loader.aspx?ParTree=15131G&i={code}"
            else:  # The adjusted data for this code is updateed
                return
        except Exception as e:
            print(f"Error on formating adjusted:{str(e)}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()

        df = pd.read_html(data)[0]
        df.columns = ["dtyyyymmdd", "new_price", "old_price"]
        df["dtyyyymmdd"] = (
            df.dtyyyymmdd
            .jalali.parse_jalali("%Y/%m/%d")
            .jalali.to_gregorian()
            .apply(lambda x: x.strftime("%Y%m%d"))
            .astype(int)
        )
        df["code"] = code
        try:
            q = f"select dtyyyymmdd as date from stock_adjusted where code = '{code}'"
            temp = pd.read_sql(q, db.engine)
            df = df[~df.dtyyyymmdd.isin(temp.date)]
        except:
            pass

        df.to_sql(
            "stock_adjusted", 
            db.engine,
            if_exists="append",
            index=False
        )
        return True, code

    except Exception as e:
        return e, code


def update_group_adjusted(code):
    """
    Update and download data of all stocks in a group.

    `Warning: Stock table should be updated`
    """
    stocks = db.session.query(Stocks.code).filter_by(group_code=code).all()
    print("updating group", code, end="\r")
    loop = asyncio.get_event_loop()
    tasks = [update_stock_adjusted(stock[0]) for stock in stocks]
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
        print("from codal_tsetmc.download import get_all_adjusted")
        print("get_all_adjusted()")
        print("```")
        raise RuntimeError

    print("group", code, "updated", end="\r")
    return results


def get_all_adjusted():
    codes = db.session.query(db.distinct(Stocks.group_code)).all()
    for i, code in enumerate(codes):
        print(
            f"{' '*18} total progress: {100*(i+1)/len(codes):.2f}%",
            end="\r",
        )
        update_group_adjusted(code[0])

    print("Adjusted Download Finished.", " "*20)
