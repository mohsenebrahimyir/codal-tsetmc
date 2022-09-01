from datetime import datetime
import asyncio
import aiohttp
import pandas as pd
import requests
import io

import codal_tsetmc.config as db
from codal_tsetmc.models import Stocks


def value_to_float(x):
    x = x.replace(",", "")
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace(' K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace(' M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace(' B', '')) * 1000000000
    return 0.0


def get_stock_capital_history(stock_id: str) -> pd.DataFrame:
    """Get stock capital from the web.

    params:
    ----------------
    code: int
        http://tsetmc.com/Loader.aspx?ParTree=15131H&i=46348559193224090#
        interger after i=

    return:
    ----------------
    pd.DataFrame
        dtyyyymmdd: str
        old_capital = int
        new_capital = int

    example
    ----------------
    df = get_stock_capital_history("46348559193224090")
    """
    url = f"http://tsetmc.com/Loader.aspx?ParTree=15131H&i={stock_id}"
    r = requests.get(url)
    df = pd.read_html(r.text)[0]
    df.columns = ["date", "new_capital", "old_capital"]
    df["new_capital"] = df["new_capital"].apply(value_to_float)
    df["old_capital"] = df["old_capital"].apply(value_to_float)
    df["date"] = df.date.jalali.parse_jalali("%Y/%m/%d")
    df["dtyyyymmdd"] = (
        df.date.jalali
        .to_gregorian()
        .apply(lambda x: x.strftime("%Y%m%d"))
        .astype(int)
    )

    return df


async def update_stock_capital(code: str):
    """
    Update (or download for the first time) Stock capital


    params:
    ----------------
    code: str or intege

    example
    ----------------
    `update_stock_capital('44891482026867833') #Done`
    """
    try:
        now = datetime.now().strftime("%Y%m%d")
        try:
            max_date_query = (
                f"select max(dtyyyymmdd) as date from stock_capital where code = '{code}'"
            )
            max_date = pd.read_sql(max_date_query, db.engine)
            last_date = max_date.date.iat[0]
        except Exception as e:
            last_date = None
        try:
            # need to updata new capital data
            if last_date is None or str(last_date) < now:
                url = f"http://tsetmc.com/Loader.aspx?ParTree=15131H&i={code}"
            else:  # The capital data for this code is updateed
                return
        except Exception as e:
            print(f"Error on formating capital:{str(e)}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()

        df = pd.read_html(data)[0]

        df.columns = ["dtyyyymmdd", "new_capital", "old_capital"]
        df["new_capital"] = df["new_capital"].apply(value_to_float)
        df["old_capital"] = df["old_capital"].apply(value_to_float)
        df["dtyyyymmdd"] = (
            df.dtyyyymmdd
            .jalali.parse_jalali("%Y/%m/%d")
            .jalali.to_gregorian()
            .apply(lambda x: x.strftime("%Y%m%d"))
            .astype(int)
        )
        df["code"] = code

        try:
            q = f"select dtyyyymmdd as date from stock_capital where code = '{code}'"
            temp = pd.read_sql(q, db.engine)
            df = df[~df.dtyyyymmdd.isin(temp.date)]
        except:
            pass

        df.to_sql(
            "stock_capital",
            db.engine,
            if_exists="append",
            index=False
        )
        return True, code

    except Exception as e:
        return e, code


def update_group_capital(code):
    """
    Update and download data of all stocks in a group.

    `Warning: Stock table should be updated`
    """
    stocks = db.session.query(Stocks.code).filter_by(group_code=code).all()
    print("updating group", code, end="\r")
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
            f"{' '*18} total progress: {100*(i+1)/len(codes):.2f}%",
            end="\r",
        )
        update_group_capital(code[0])

    print("Capital Download Finished.", " "*20)
