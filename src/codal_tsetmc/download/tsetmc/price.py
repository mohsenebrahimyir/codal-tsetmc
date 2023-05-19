from jdatetime import date as jdate
from jdatetime import datetime as jdt
from datetime import datetime
import asyncio
import aiohttp
import pandas as pd
import io
import requests

import codal_tsetmc.config as db
from codal_tsetmc.models.stocks import Stocks
from codal_tsetmc.tools import *
from codal_tsetmc.download.tsetmc.stock import is_stock_in_bourse_or_fara_or_paye



def get_index_prices_history():
    code = "32097828799138957"
    url = f'http://www.tsetmc.com/tsev2/chart/data/Index.aspx?i={code}&t=value'
    s = requests.get(url, verify=False).content
    df = pd.read_csv(io.StringIO(s.decode("utf-8").replace(";", "\n")), header=None)
    df.columns = ["date", "price"]
    df["date"] = df["date"].jalali.parse_jalali("%Y/%m/%d").apply(lambda x: x.strftime('%Y%m%d000000'))
    df["code"] = code
    df["ticker"] = "INDEX"
    df = df.sort_values("date")

    return df

def update_index_prices():
    index = "32097828799138957"
    df = get_index_prices_history()
    df["up_date"] = jdt.now().strftime("%Y%m%d000000")
    fill_table_of_db_with_df(
        df, 
        columns="date",
        table="stock_price",
        conditions=f"where code = '{index}'",
        text=f"stock: {index}"
    )


def get_stock_price_daily(code: str, date: str):
    data = "ClosingPrice/GetClosingPriceDaily"
    dict_data = get_data_from_cdn_tsetmec_api(data, code, date)
    
    return dict_data["closingPriceDaily"]["pClosing"]

def cleanup_stock_prices_records(response):
    df = pd.read_csv(io.StringIO(response))
    df.columns = [i[1:-1].lower() for i in df.columns]
    df["date"] = df["dtyyyymmdd"].apply(lambda x: datetime.strptime(str(x), "%Y%m%d"))
    df["date"] = df["date"].jalali.to_jalali().apply(lambda x: x.strftime('%Y%m%d000000'))
    df["price"] = df["close"]
    df = df.sort_values("date")

    return df[["date", "ticker", "price"]]

def get_stock_prices_history(code: str, from_date="20000101", to_date=datetime.now().strftime("%Y%m%d")) -> pd.DataFrame:
    url = f"http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={code}&DateFrom={from_date}&DateTo={to_date}&b=0"
    response = requests.get(url).text
    df = cleanup_stock_prices_records(response)
    df["code"] = code

    return df




async def update_stock_prices(code: str):
    try:
        if not is_stock_in_bourse_or_fara_or_paye(code):
            return
        
        now = datetime.now().strftime("%Y%m%d")
        try:
            query_index = f"select max(date) as date from stock_price where ticker = INDEX"
            max_date_index = pd.read_sql(query_index, db.engine)
            last_date_index = max_date_index.date.iat[0]

            if last_date_index is None:
                update_index_prices()
                max_date_index = pd.read_sql(query_index, db.engine)
                last_date_index = max_date_index.date.iat[0]

            query_stock = f"select max(date) as date from stock_price where code = {code}"
            max_date_stock = pd.read_sql(query_stock, db.engine)
            last_date_stock = max_date_stock.date.iat[0]

            if last_date_index < last_date_stock:
                update_index_prices()
                max_date_index = pd.read_sql(query_index, db.engine)
                last_date_index = max_date_index.date.iat[0]

        except Exception as e:
            last_date_stock = None
        try:
            if last_date_stock is None:  # no any record added in database
                url = f"http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={code}&DateFrom=20000101&DateTo={now}&b=0"
            elif last_date_stock < last_date_index:  # need to updata new price data
                last_date = jdt.strptime(str(int(last_date_stock)), "%Y%m%d%H%M%S").togregorian().strftime("%Y%m%d")
                url = f"http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={code}&DateFrom={str(last_date)}&DateTo={now}&b=0"
            else:  # The price data for this code is updateed
                return
        except Exception as e:
            print(f"Error on formating price:{str(e)}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.text()

        df = cleanup_stock_prices_records(response)
        df["code"] = code
        df["up_date"] = jdt.now().strftime("%Y%m%d000000")

        fill_table_of_db_with_df(
            df, 
            columns="date",
            table="stock_price",
            conditions=f"where code = '{code}'",
            text=f"stock: {code}"
        )

        return True, code

    except Exception as e:
        return e, code

def update_stocks_prices(codes, msg=""):
    loop = asyncio.get_event_loop()
    tasks = [update_stock_prices(code) for code in codes]
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


def update_stocks_group_prices(group_code):
    stocks = db.session.query(Stocks.code).filter_by(group_code=group_code).all()
    print(f"{' '*25} group: {group_code}", end="\r")
    codes = [stock[0] for stock in stocks]
    msg = "group " + group_code + " updated"
    results = update_stocks_prices(codes, msg)
    return results


def fill_stocks_prices_table():
    update_index_prices()
    codes = db.session.query(db.distinct(Stocks.group_code)).all()
    for i, code in enumerate(codes):
        print(
            f"{' '*35} total progress: {100*(i+1)/len(codes):.2f}%",
            end="\r",
        )
        update_stocks_group_prices(code[0])
    print("Price Download Finished.", " "*50)

