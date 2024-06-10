from jdatetime import datetime as jdt
import aiohttp
import nest_asyncio
import jalali_pandas
import pandas as pd
import requests

from codal_tsetmc import CommoditiesPrices
from codal_tsetmc.config.engine import engine
from codal_tsetmc.tools.database import fill_table_of_db_with_df
from codal_tsetmc.tools.api import (
    get_csv_from_github,
    get_results_by_asyncio_loop
)


def cleanup_commodity_price_records(response) -> pd.DataFrame:
    res_dict = response.json()["data"]
    df = pd.DataFrame.from_records(res_dict)
    df.columns = [
        "open", "low",
        "high", "close",
        "change_amount",
        "change_percent",
        "gdate", "jdate"
    ]
    df["date"] = df["jdate"].jalali.parse_jalali("%Y/%m/%d").apply(lambda x: x.strftime('%Y%m%d000000'))
    df["price"] = pd.to_numeric(df["close"].str.replace(",", ""))

    df = df.sort_values("date")

    return df[["date", "price"]]


def get_commodity_price_history(symbol: str) -> pd.DataFrame:
    df = None
    url = f"https://api.tgju.org/v1/market/indicator/summary-table-data/{symbol}"
    response = requests.get(url, params=[], headers={})  # ('length', '100'),
    new = cleanup_commodity_price_records(response)
    if symbol == "price_dollar_rl":
        old = get_csv_from_github(symbol)
        old["date"] = old["date"].jalali.parse_jalali("%Y/%m/%d").apply(lambda x: x.strftime('%Y%m%d000000'))

        df = pd.concat(new, old[~old["date"].isin(new["date"])])

    df["symbol"] = symbol
    df.sort_values("date")
    df = df.set_index("date")

    return df


async def update_commodity_prices(symbol: str):
    nest_asyncio.apply()

    days = None
    url = ""
    try:
        now = jdt.now()
        try:
            query = f"select max(date) as date from commodity_price where symbol = '{symbol}'"
            max_date = pd.read_sql(query, engine)
            last_date = max_date.date.iat[0]
            days = now - jdt.strptime(last_date, "%Y%m%d%H%M%S")

        except Exception as e:
            print(e)
            last_date = None
        try:
            if last_date is None:
                url = f"https://api.tgju.org/v1/market/indicator/summary-table-data/{symbol}"
            elif days.days > 0:
                url = f"https://api.tgju.org/v1/market/indicator/summary-table-data/{symbol}?length={days.days}"
            else:  # The price data for this symbol is updated
                return
        except Exception as e:
            print(f"Error on formatting price:{str(e)}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                response = await resp.json()

        df = cleanup_commodity_price_records(response)
        df["symbol"] = symbol
        df["up_date"] = now.strftime("%Y%m%d000000")

        try:
            CommoditiesPrices.__table__.create(engine)
        except Exception as e:
            print(e.__context__, end="\r", flush=True)

        fill_table_of_db_with_df(
            df,
            columns="date",
            table="commodities_prices",
            conditions=f"where symbol = '{symbol}'"
        )

        return True, symbol

    except Exception as e:
        return e, symbol


def update_commodities_prices(symbols):
    print(f"{' ' * 25} update Commodities ", end="\r")
    tasks = [update_commodity_prices(symbol) for symbol in symbols]
    get_results_by_asyncio_loop(tasks)


def fill_commodities_prices_table():
    symbols = ["price_dollar_rl"]
    for i, symbol in enumerate(symbols):
        print(f"{' ' * 35} total progress: {100 * (i + 1) / len(symbols):.2f}%", end="\r")
        if symbol == "price_dollar_rl":

            query = f"select min(date) as date from commodity_price where symbol = '{symbol}'"
            min_date = pd.read_sql(query, engine)
            first_date = min_date.date.iat[0]
            if first_date != "13600707000000":
                df = get_csv_from_github(symbol)
                df["date"] = df["date"].jalali.parse_jalali("%Y/%m/%d").apply(lambda x: x.strftime('%Y%m%d000000'))
                df["symbol"] = symbol
                df["up_date"] = jdt.now().strftime("%Y%m%d000000")

                try:
                    CommoditiesPrices.__table__.create(engine)
                except Exception as e:
                    print(e.__context__, end="\r", flush=True)

                fill_table_of_db_with_df(
                    df,
                    columns="date",
                    table="commodities_prices",
                    conditions=f"where symbol = '{symbol}'"
                )

        update_commodities_prices([symbol])
    print("Price Download Finished.", " " * 50)
