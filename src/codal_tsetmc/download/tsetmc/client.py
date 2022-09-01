from datetime import datetime
import asyncio
import aiohttp
import pandas as pd
import requests
import io

import codal_tsetmc.config as db
from codal_tsetmc.models import Stocks


def get_stock_client_history(stock_id: str) -> pd.DataFrame:
    """Get stock client from the web.

    params:
    ----------------
    stock_id: int
        http://www.tsetmc.com/tsev2/data/clienttype.aspx?i=35700344742885862
        number after i=

    return:
    ----------------
    pd.DataFrame
        dtyyyymmdd: str
        natural_buy_count: int
        legal_buy_count: int
        natural_sell_count: int
        legal_sell_count: int
        natural_buy_volume: int
        legal_buy_volume: int
        natural_sell_volume: int
        legal_sell_volume: int
        natural_buy_value: int
        legal_buy_value: int
        natural_sell_value: int
        legal_sell_value: int
        volume: int

    example
    ----------------
    df = get_stock_client_history("35700344742885862")
    """
    url = f"http://www.tsetmc.com/tsev2/data/clienttype.aspx?i={stock_id}"
    r = requests.get(url).content.decode("utf-8").replace(";", "\n")
    df = pd.read_csv(io.StringIO(r), header=None)
    df.columns = [
        "dtyyyymmdd",
        "natural_buy_count",
        "legal_buy_count",
        "natural_sell_count",
        "legal_sell_count",
        "natural_buy_volume",
        "legal_buy_volume",
        "natural_sell_volume",
        "legal_sell_volume",
        "natural_buy_value",
        "legal_buy_value",
        "natural_sell_value",
        "legal_sell_value",
    ]
    return df


async def update_stock_client(code: str):
    """
    Update (or download for the first time) Stock clients


    params:
    ----------------
    code: str or int

    example
    ----------------
    `update_stock_client('44891482026867833') #Done`
    """
    try:
        now = datetime.now().strftime("%Y%m%d")
        try:
            max_date_query = (
                f"select max(dtyyyymmdd) as date from stock_client where code = '{code}'"
            )
            max_date = pd.read_sql(max_date_query, db.engine)
            last_date = max_date.date.iat[0]
        except Exception as e:
            last_date = None
        try:
            # need to updata new client data
            if last_date is None or str(last_date) < now:
                url = f"http://www.tsetmc.com/tsev2/data/clienttype.aspx?i={code}"
            else:  # The client data for this code is updateed
                return
        except Exception as e:
            print(f"Error on formating client:{str(e)}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()
        
        data = data.replace(";", "\n")
        df = pd.read_csv(io.StringIO(data), header=None)
        df.columns = [
            "dtyyyymmdd",
            "natural_buy_count",
            "legal_buy_count",
            "natural_sell_count",
            "legal_sell_count",
            "natural_buy_volume",
            "legal_buy_volume",
            "natural_sell_volume",
            "legal_sell_volume",
            "natural_buy_value",
            "legal_buy_value",
            "natural_sell_value",
            "legal_sell_value",
        ]
        df["code"] = code
        try:
            q = f"select dtyyyymmdd as date from stock_client where code = '{code}'"
            temp = pd.read_sql(q, db.engine)
            df = df[~df.dtyyyymmdd.isin(temp.date)]
        except:
            pass

        df.to_sql(
            "stock_client", 
            db.engine,
            if_exists="append",
            index=False
        )
        return True, code

    except Exception as e:
        return e, code


def update_group_client(code):
    """
    Update and download data of all stocks in a group.

    `Warning: Stock table should be updated`
    """
    stocks = db.session.query(Stocks.code).filter_by(group_code=code).all()
    print("updating group", code, end="\r")
    loop = asyncio.get_event_loop()
    tasks = [update_stock_client(stock[0]) for stock in stocks]
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
        print("from codal_tsetmc.download import get_all_client")
        print("get_all_client()")
        print("```")
        raise RuntimeError

    print("group", code, "updated", end="\r")
    return results


def get_all_client():
    codes = db.session.query(db.distinct(Stocks.group_code)).all()
    for i, code in enumerate(codes):
        print(
            f"{' '*18} total progress: {100*(i+1)/len(codes):.2f}%",
            end="\r",
        )
        update_group_client(code[0])

    print("Client Download Finished.", " "*20)
