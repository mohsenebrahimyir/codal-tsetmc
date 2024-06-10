from jdatetime import datetime as jdt
import jalali_pandas
import aiohttp
import nest_asyncio
import pandas as pd
import requests
import io
from codal_tsetmc.config.engine import session, engine
from codal_tsetmc.models.stocks import Stocks, StocksCapitals
from codal_tsetmc.tools.database import fill_table_of_db_with_df, read_table_by_conditions
from codal_tsetmc.tools.api import (
    get_data_from_cdn_tsetmec_api,
    get_results_by_asyncio_loop
)
from codal_tsetmc.tools.string import value_to_float
from codal_tsetmc.download.tsetmc.stock import is_stock_in_bourse_or_fara_or_paye


def get_stock_capital_daily(code: str):
    data = "Instrument/GetInstrumentInfo"
    dict_data = get_data_from_cdn_tsetmec_api(data, code, "")
    return dict_data["instrumentInfo"]["zTitad"]


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
    df = df[(df.old == df.new.shift(fill_value=0)) | (df.old == min(df.old)) | (df.new == max(df.new))]

    df = df.sort_values("date")

    return df


def get_stock_capitals_history(code: str) -> pd.DataFrame:
    url = f"http://old.tsetmc.com/Loader.aspx?ParTree=15131H&i={code}"
    response = requests.get(url).text
    df = cleanup_stock_capitals_records(response)
    df["code"] = code
    stock = Stocks.query.filter_by(code=code).first()
    df["symbol"] = stock.symbol

    return df


async def update_stock_capitals_async(code: str):
    nest_asyncio.apply()

    try:
        if is_stock_in_bourse_or_fara_or_paye(code):
            try:
                def get_max_date():
                    return read_table_by_conditions(
                        table="stocks_capitals",
                        variable="code",
                        value=code,
                        columns="max(date) AS date"
                    )

                last_up_date = get_max_date().up_date.iat[0]

            except Exception as e:
                print(' ' * 25, "\r", e.__context__, flush=True, end='\r')
                last_up_date = "0"

            jnow = jdt.now().strftime("%Y%m%d000000")
            url = ""
            try:
                # need to update new capital data
                if last_up_date is None or last_up_date < jnow:
                    url = f"http://old.tsetmc.com/Loader.aspx?ParTree=15131H&i={code}"
                else:  # The capital data for this code is updated
                    return
            except Exception as e:
                print(f"Error on formatting capital:{str(e)}")

            async with aiohttp.ClientSession() as ses:
                async with ses.get(url) as resp:
                    response = await resp.text()

            df = cleanup_stock_capitals_records(response)

            df["code"] = code
            stock = Stocks.query.filter_by(code=code).first()
            df["symbol"] = stock.symbol
            df["up_date"] = jnow

            try:
                StocksCapitals.__table__.create(engine)
            except Exception as e:
                print(e.__context__, end="\r", flush=True)

            fill_table_of_db_with_df(
                df,
                columns="date",
                table="stocks_capitals",
                conditions=f"where code = '{code}'"
            )

        print(' ' * 25, "\r", code, flush=True, end='\r')

    except Exception as e:
        print(' ' * 25, "\r", e.__context__, flush=True, end='\r')


def update_stocks_capitals(codes):
    tasks = [update_stock_capitals_async(code) for code in codes]
    get_results_by_asyncio_loop(tasks)


def update_stock_capitals(code):
    update_stocks_capitals([code])


def update_stocks_group_capitals(group_code):
    stocks = session.query(Stocks.code).filter_by(group_code=group_code).all()
    print(f"{' ' * 25} group: {group_code}", flush=True, end='\r')
    codes = [stock[0] for stock in stocks]
    update_stocks_capitals(codes)


def fill_stocks_capitals_table():
    codes = session.query(Stocks.group_code).distinct().all()
    for i, code in enumerate(codes):
        print(
            f"{' ' * 35} total progress: {100 * (i + 1) / len(codes):.2f}%",
            flush=True, end='\r',
        )
        update_stocks_group_capitals(code[0])

    print("Capital Download Finished.", " " * 50)
