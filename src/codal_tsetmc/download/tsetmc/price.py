from time import time

from jdatetime import datetime as jdt
from datetime import datetime
import jalali_pandas
import aiohttp
import nest_asyncio
import pandas as pd
import io
import requests
from codal_tsetmc.config.engine import session, engine
from codal_tsetmc.download.tsetmc.stock import is_stock_in_bourse_or_fara_or_paye
from codal_tsetmc.models.stocks import Stocks, StocksPrices
from codal_tsetmc.tools.database import (
    fill_table_of_db_with_df, read_table_by_conditions, is_table_exist_in_db
)
from codal_tsetmc.tools.api import (
    get_data_from_cdn_tsetmec_api, get_results_by_asyncio_loop, GET_HEADERS_REQUEST
)

INDEX_CODE = "32097828799138957"


def edit_index_prices(data, code, symbol):
    df = pd.DataFrame(data["indexB2"])[["dEven", "xNivInuClMresIbs"]]
    df.columns = ["date", "price"]
    df["date"] = df["date"].apply(lambda x: datetime.strptime(str(x), "%Y%m%d"))
    df["date"] = df["date"].jalali.to_jalali().apply(lambda x: x.strftime('%Y%m%d000000'))
    df["code"] = code
    df["symbol"] = symbol
    df["value"] = pd.NA
    df["volume"] = pd.NA
    df["up_date"] = jdt.now().strftime("%Y%m%d000000")
    df = df.sort_values("date")

    return df


def get_index_prices_history(code: str = INDEX_CODE, symbol: str = "شاخص كل6") -> pd.DataFrame:
    url = f'http://cdn.tsetmc.com/api/Index/GetIndexB2History/{code}'
    data = requests.get(url, headers=GET_HEADERS_REQUEST).json()
    df = edit_index_prices(data, code, symbol)

    return df


async def update_index_prices_async(code):
    nest_asyncio.apply()
    url = f'http://cdn.tsetmc.com/api/Index/GetIndexB2History/{code}'
    try:
        async with aiohttp.ClientSession() as ses:
            async with ses.get(url, headers=GET_HEADERS_REQUEST) as resp:
                data = await resp.json()

        stock = Stocks.query.filter_by(code=code).first()
        df = edit_index_prices(data, code, stock.symbol)

        if not is_table_exist_in_db(StocksPrices.__tablename__):
            StocksPrices.__table__.create(engine)

        fill_table_of_db_with_df(
            df[["date", "symbol", "code", "price", "volume", "value", "up_date"]],
            columns="date",
            table=StocksPrices.__tablename__,
            conditions=f"where code = '{code}'"
        )
        print(f"Stock prices updated. (code: {stock.code}, symbol: {stock.symbol})")
    except Exception as e:
        print(e.__context__)
        return False

    return True


def update_indexes_prices(codes=None):
    if codes is None:
        codes = [INDEX_CODE]
    tasks = [update_index_prices_async(code) for code in codes]
    get_results_by_asyncio_loop(tasks)


def update_index_prices(code=None):
    if code is None:
        code = INDEX_CODE
    update_indexes_prices([code])


def get_stock_price_daily(code: str, date: str = None):
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
        
    data = "ClosingPrice/GetClosingPriceDaily"
    dict_data = get_data_from_cdn_tsetmec_api(data, code, date)

    return dict_data["closingPriceDaily"]["pClosing"]


def cleanup_stock_prices_records(data):
    df = pd.read_csv(io.StringIO(data), delimiter="@", lineterminator=";", engine="c", header=None)
    df.columns = "date high low price close open yesterday value volume count".split()
    df["date"] = df["date"].apply(lambda x: datetime.strptime(str(x), "%Y%m%d"))
    df["date"] = df["date"].jalali.to_jalali().apply(lambda x: x.strftime('%Y%m%d000000'))
    df = df.sort_values("date")

    return df[["date", "volume", "value", "price"]]


def get_stock_prices_history(code: str) -> pd.DataFrame:
    url = f"http://old.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={code}&Top=999999&A=0"
    data = requests.get(url).text
    df = pd.read_csv(io.StringIO(data), delimiter="@", lineterminator=";", engine="c", header=None)
    df.columns = "date high low price close open yesterday value volume count".split()
    df["date"] = df["date"].apply(lambda x: datetime.strptime(str(x), "%Y%m%d"))
    df["code"] = code

    return df


async def update_stock_prices_async(code: str):
    if not is_stock_in_bourse_or_fara_or_paye(code):
        return True

    if not is_table_exist_in_db(StocksPrices.__tablename__):
        StocksPrices.__table__.create(engine)

    stock = Stocks.query.filter_by(code=code).first()
    try:
        try:
            def get_max_date_stock():
                return read_table_by_conditions(
                    table=StocksPrices.__tablename__,
                    variable="code",
                    value=code,
                    columns="max(date) AS date"
                )

            def get_max_date_index():
                return read_table_by_conditions(
                    table=StocksPrices.__tablename__,
                    variable="code",
                    value=INDEX_CODE,
                    columns="max(date) AS date"
                )

            last_date_stock = get_max_date_stock().date.iat[0]
            last_date_index = get_max_date_index().date.iat[0]

            if last_date_index is None or (last_date_stock is not None and int(last_date_index) < int(last_date_stock)):
                update_indexes_prices()
                last_date_index = get_max_date_index().date.iat[0]

        except Exception as e:
            print(e.__context__)
            print("Missing in last date stocks")
            last_date_stock = "0"
            last_date_index = "0"

        if last_date_stock is None:
            url = (
                f"http://old.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={code}&Top=999999&A=0"
            )
        elif int(last_date_stock) < int(last_date_index):  # need to update new price data
            days = (
                    jdt.strptime(str(int(last_date_index)), "%Y%m%d%H%M%S") -
                    jdt.strptime(str(int(last_date_stock)), "%Y%m%d%H%M%S")
            ).days
            url = (
                f"http://old.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={code}&Top={days}&A=0"
            )

        else:
            print(f"Stock prices already updated. (code: {stock.code}, symbol: {stock.symbol})")
            return True

        nest_asyncio.apply()
        async with aiohttp.ClientSession() as ses:
            async with ses.get(url, headers=GET_HEADERS_REQUEST) as resp:
                data = await resp.text()

        df = cleanup_stock_prices_records(data)
        df["code"] = code
        df["symbol"] = stock.symbol
        df["up_date"] = jdt.now().strftime("%Y%m%d000000")

        fill_table_of_db_with_df(
            df,
            columns="date",
            table=StocksPrices.__tablename__,
            conditions=f"where code = '{code}'"
        )
        print(f"Stock prices updated. (code: {stock.code}, symbol: {stock.symbol})")
        return True

    except Exception as e:
        print(f"Stock prices Failed. (code: {stock.code}, symbol: {stock.symbol})", e.__context__)
        return False


def update_stocks_prices(codes):
    tasks = [update_stock_prices_async(code) for code in codes]
    get_results_by_asyncio_loop(tasks)


def update_stock_prices(code):
    update_stocks_prices([code])


def update_stocks_group_prices(group_code):
    stocks = session.query(Stocks.code).filter_by(group_code=group_code).all()
    print(f"Started group: {group_code}")
    codes = [stock[0] for stock in stocks]
    update_stocks_prices(codes)
    print(f"Finished group: {group_code}")


def fill_stocks_prices_table():
    start_time = time()
    update_indexes_prices()
    codes = session.query(Stocks.group_code).distinct().all()
    for i, code in enumerate(codes):
        print(f"Total progress: {100 * (i + 1) / len(codes):.2f}%")
        update_stocks_group_prices(code[0])

    print("Stocks Prices Download is Finished.")
    print(f"Total time: {time() - start_time:.2f} seconds")
