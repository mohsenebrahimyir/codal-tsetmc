from time import time

from jdatetime import datetime as jdt
# noinspection PyUnresolvedReferences
import jalali_pandas
import aiohttp
import nest_asyncio
import pandas as pd
import requests
import io
from codal_tsetmc.config.engine import session
from codal_tsetmc.models import Stock, StockCapital
from codal_tsetmc.tools.database import fill_table_of_db_with_df, read_table_by_sql_query, create_table_if_not_exist
from codal_tsetmc.tools.api import (
    get_data_from_cdn_tsetmec_api,
    get_results_by_asyncio_loop
)
from codal_tsetmc.tools.string import value_to_float, datetime_to_num
from codal_tsetmc.download.tsetmc.stock import is_stock_in_bourse_or_fara_or_paye


def get_stock_capital_daily(code: str):
    data = "Instrument/GetInstrumentInfo"
    dict_data = get_data_from_cdn_tsetmec_api(data, code, "")
    return dict_data["instrumentInfo"]["zTitad"]


def cleanup_stock_capitals_records(response):
    df = pd.read_html(io.StringIO(response))[0]
    df.columns = ["date", "new", "old"]
    df["date"] = (
        df["date"]
        .jalali.parse_jalali("%Y/%m/%d")
        .apply(lambda x: x.strftime('%Y%m%d000000'))
        .apply(datetime_to_num)
    )
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
    stock = Stock.query.filter_by(code=code).first()
    df["symbol"] = stock.symbol

    return df


async def update_stock_capitals_async(code: str):

    if not is_stock_in_bourse_or_fara_or_paye(code):
        return True
    create_table_if_not_exist(StockCapital)

    stock = Stock.query.filter_by(code=code).first()
    try:
        query = f"SELECT max(up_date) AS up_date FROM {StockCapital.__tablename__} WHERE code = '{code}'"
        max_date = read_table_by_sql_query(query)
        if not max_date.empty or max_date.up_date.iat[0] is not None:
            last_up_date = max_date.up_date.iat[0]
        else:
            last_up_date = "0"

        jnow = jdt.now().strftime("%Y%m%d000000")
        if last_up_date is None or last_up_date < jnow:
            url = f"http://old.tsetmc.com/Loader.aspx?ParTree=15131H&i={code}"
        elif last_up_date > jnow:
            print(f"Stock Capital already updated. (code: {stock.code}, symbol: {stock.symbol})")
            return True
        else:
            return False

        nest_asyncio.apply()
        async with aiohttp.ClientSession() as ses:
            async with ses.get(url) as resp:
                response = await resp.text()

        df = cleanup_stock_capitals_records(response)
        if df.empty:
            print(f"Stock Capital is empty. (code: {stock.code}, symbol: {stock.symbol})")
            return True

        df["code"] = code
        df["symbol"] = stock.symbol
        df["up_date"] = jnow.apply(datetime_to_num)

        fill_table_of_db_with_df(
            df,
            columns="date",
            table=StockCapital.__tablename__,
            conditions=f"where code = '{code}'"
        )

        print(f"Stock Capital updated. (code: {stock.code}, symbol: {stock.symbol})")
        return True

    except Exception as e:
        print(f"Stock Capital Failed. (code: {stock.code}, symbol: {stock.symbol})", e.__context__)
        return False


def update_stocks_capitals(codes):
    tasks = [update_stock_capitals_async(code) for code in codes]
    get_results_by_asyncio_loop(tasks)


def update_stock_capitals(code):
    update_stocks_capitals([code])


def update_stocks_group_capitals(group_code):
    stocks = session.query(Stock.code).filter_by(group_code=group_code).all()
    print(f"Stocks group: {group_code} Started.")
    codes = [stock[0] for stock in stocks]
    update_stocks_capitals(codes)
    print("Stocks group:", group_code, "Finished.")


def fill_stocks_capitals_table():
    start_time = time()
    codes = session.query(Stock.group_code).distinct().all()
    for i, code in enumerate(codes):
        print(f"Total progress: {100 * (i + 1) / len(codes):.2f}%")
        update_stocks_group_capitals(code[0])

    print("Stocks Capitals Download is Finished.")
    print(f"Total time: {time() - start_time:.2f} seconds")
