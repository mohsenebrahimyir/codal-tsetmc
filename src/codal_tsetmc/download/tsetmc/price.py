from time import time
import io

from jdatetime import datetime as jdt
from datetime import datetime
# noinspection PyUnresolvedReferences
import jalali_pandas
import aiohttp
import nest_asyncio
import pandas as pd
import requests

from codal_tsetmc.tools.string import datetime_to_num
from codal_tsetmc.config.engine import session
from codal_tsetmc.download.tsetmc.stock import is_stock_in_bourse_or_fara_or_paye
from codal_tsetmc.models import Stock, StockPrice
from codal_tsetmc.tools.database import (
    fill_table_of_db_with_df, read_table_by_conditions, create_table_if_not_exist
)
from codal_tsetmc.tools.api import (
    get_data_from_cdn_tsetmec_api, get_results_by_asyncio_loop, GET_HEADERS_REQUEST
)

INDEX_CODE = "32097828799138957"


def edit_index_prices(data, code, symbol):
    df = pd.DataFrame(data["indexB2"])[["dEven", "xNivInuClMresIbs"]]
    df.columns = ["date", "price"]
    df["date"] = df["date"].apply(lambda x: datetime.strptime(str(x), "%Y%m%d"))
    df["date"] = df["date"].jalali.to_jalali().apply(lambda x: x.strftime('%Y%m%d000000')).apply(datetime_to_num)
    df["code"] = code
    df["symbol"] = symbol
    df["value"] = pd.NA
    df["volume"] = pd.NA
    df["up_date"] = jdt.now().strftime("%Y%m%d000000").apply(datetime_to_num)
    df = df.sort_values("date")

    return df


def get_index_prices_history(code: str = INDEX_CODE, symbol: str = "شاخص كل6") -> pd.DataFrame:
    url = f'http://cdn.tsetmc.com/api/Index/GetIndexB2History/{code}'
    data = requests.get(url, headers=GET_HEADERS_REQUEST).json()
    df = edit_index_prices(data, code, symbol)

    return df


async def update_index_prices_async(code):
    create_table_if_not_exist(StockPrice)
    url = f'http://cdn.tsetmc.com/api/Index/GetIndexB2History/{code}'
    try:
        nest_asyncio.apply()
        async with aiohttp.ClientSession() as ses:
            async with ses.get(url, headers=GET_HEADERS_REQUEST) as resp:
                data = await resp.json()

        stock = Stock.query.filter_by(code=code).first()
        df = edit_index_prices(data, code, stock.symbol)[StockPrice.__table__.columns.keys()[1:]]

        fill_table_of_db_with_df(
            df, columns="date", table=StockPrice.__tablename__, conditions=f"where code = '{code}'"
        )
        print(f"Stock prices updated. (code: {stock.code}, symbol: {stock.symbol})")
        return True
    except Exception as e:
        print(e.__context__)
        return False


def update_indexes_prices(codes: list = None):
    if codes is None:
        codes = [INDEX_CODE]
    tasks = [update_index_prices_async(code) for code in codes]
    results = get_results_by_asyncio_loop(tasks)
    return results


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
    df["date"] = (
        df["date"]
        .apply(lambda x: datetime.strptime(str(x), "%Y%m%d"))
        .jalali.to_jalali()
        .apply(lambda x: x.strftime('%Y%m%d000000'))
        .apply(datetime_to_num)
    )
    df = df.sort_values("date")

    return df[["date", "volume", "value", "price"]]


def get_stock_prices_history(code: str) -> pd.DataFrame:
    url = f"http://old.tsetmc.com/tsev2/data/InstTradeHistory.aspx?i={code}&Top=999999&A=0"
    data = requests.get(url).text
    df = pd.read_csv(io.StringIO(data), delimiter="@", lineterminator=";", engine="c", header=None)
    df.columns = "date high low price close open yesterday value volume count".split()
    df["date"] = df["date"].apply(lambda x: datetime.strptime(str(x), "%Y%m%d")).apply(datetime_to_num)
    df["code"] = code

    return df


async def update_stock_prices_async(code: str):
    if not is_stock_in_bourse_or_fara_or_paye(code):
        return True

    create_table_if_not_exist(StockPrice)
    stock = Stock.query.filter_by(code=code).first()
    try:
        try:
            def get_max_date_stock():
                return read_table_by_conditions(
                    table=StockPrice.__tablename__,
                    variable="code",
                    value=code,
                    columns="max(date) AS date"
                )

            def get_max_date_index():
                return read_table_by_conditions(
                    table=StockPrice.__tablename__,
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
        df["up_date"] = jdt.now().strftime("%Y%m%d000000").apply(datetime_to_num)

        fill_table_of_db_with_df(
            df,
            columns="date",
            table=StockPrice.__tablename__,
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
    stocks = session.query(Stock.code).filter_by(group_code=group_code).all()
    print(f"Started group: {group_code}")
    codes = [stock[0] for stock in stocks]
    update_stocks_prices(codes)
    print(f"Finished group: {group_code}")


def fill_stocks_prices_table():
    start_time = time()
    update_indexes_prices()
    codes = session.query(Stock.group_code).distinct().all()
    for i, code in enumerate(codes):
        print(f"Total progress: {100 * (i + 1) / len(codes):.2f}%")
        update_stocks_group_prices(code[0])

    print("Stocks Prices Download is Finished.")
    print(f"Total time: {time() - start_time:.2f} seconds")
