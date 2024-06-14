import sys
import asyncio
from time import time

import aiohttp
import nest_asyncio
import pandas as pd

from codal_tsetmc import Letters
from codal_tsetmc.config.engine import session, engine
from codal_tsetmc.models.stocks import Stocks
from codal_tsetmc.tools.api import GET_HEADERS_REQUEST
from codal_tsetmc.tools.string import (
    FA_TO_EN_DIGITS, LETTERS_CODE_TO_TITLE,
    datetime_to_num, df_col_to_snake_case,
)

from codal_tsetmc.tools.database import fill_table_of_db_with_df, create_table_if_not_exist
from codal_tsetmc.download.codal.query import CodalQuery

"""################
گرفتن اطلاعات از کدال
################"""


def convert_letter_list_to_df(data) -> pd.DataFrame:
    df = pd.DataFrame(data).replace(regex=FA_TO_EN_DIGITS)
    df["LetterSerial"] = df["Url"].replace(regex={
        r"^.*LetterSerial=": "",
        r"\&.*$": ""
    })
    df["LetterTypes"] = df["LetterCode"].replace(regex=LETTERS_CODE_TO_TITLE)
    df["PublishDateTime"] = df["PublishDateTime"].apply(datetime_to_num)
    df["SentDateTime"] = df["SentDateTime"].apply(datetime_to_num)
    df["LetterTitle"] = df["Title"]
    df["Name"] = df["CompanyName"]
    df = df[[
        "PublishDateTime", "SentDateTime", "TracingNo",
        "LetterSerial", "LetterCode", "LetterTypes", "LetterTitle",
        "Symbol", "Name",
    ]]
    df = df_col_to_snake_case(df)

    return df


async def get_letters_urls_from_page_100000_async(ses, url: str):
    nest_asyncio.apply()

    async with ses.get(url, cookies={}, headers=GET_HEADERS_REQUEST, data="") as response:
        data = await response.json()

    u = url.split("100000")
    return [f'{u[0]}{data["Page"] + 1 - i}{u[1]}' for i in range(1, data["Page"] + 1)]


async def get_letters_urls_async(urls: list):
    nest_asyncio.apply()

    tasks = []
    async with aiohttp.ClientSession() as ses:
        for url in urls:
            tasks.append(get_letters_urls_from_page_100000_async(ses, url))
        results = await asyncio.gather(*tasks)
    return results


def get_letter_urls_parallel(urls: list):
    nest_asyncio.apply()
    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    try:
        results = loop.run_until_complete(get_letters_urls_async(urls))
        return results

    except Exception as e:
        print(e.__context__)
        return False


def get_letters_urls(query: CodalQuery, symbols=None):
    query.set_page_number(100000)
    urls = []

    if symbols is not None:
        for symbol in symbols:
            query.set_symbol(symbol)
            urls += [query.get_query_url()]
            print(f"Set letter url for: {symbol}")
    else:
        urls = [query.get_query_url()]

    results = get_letter_urls_parallel(urls)

    return results


async def update_letters_by_url_async(ses, url: str):
    nest_asyncio.apply()

    try:
        async with ses.get(url, cookies={}, headers=GET_HEADERS_REQUEST, data="") as response:
            data = await response.json()

        model = Letters
        create_table_if_not_exist(model)
        df = convert_letter_list_to_df(data["Letters"])

        fill_table_of_db_with_df(df, model.__tablename__, "tracing_no")
        return True
    except Exception as e:
        print(e.__context__)
        return False


async def update_letters_by_urls_async(urls: list):
    nest_asyncio.apply()

    tasks = []
    async with aiohttp.ClientSession() as ses:
        for url in urls:
            tasks.append(update_letters_by_url_async(ses, url))
        await asyncio.gather(*tasks)


def update_letter_table_by_urls(urls: list):
    nest_asyncio.apply()

    if sys.platform == 'win32':
        ##############################################################################
        from functools import wraps

        from asyncio.proactor_events import _ProactorBasePipeTransport

        def silence_event_loop_closed(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                try:
                    return func(self, *args, **kwargs)
                except RuntimeError as ru:
                    if str(ru) != 'Event loop is closed':
                        raise

            return wrapper

        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)

        ##############################################################################
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(update_letters_by_urls_async(urls))
        loop.close()
        return True
    except Exception as e:
        print(e.__context__)
        return False


def update_letters_table(query: CodalQuery, symbols: list = None):
    urls_list = get_letters_urls(query, symbols)

    letter_urls = []
    for urls in urls_list:
        for url in urls:
            letter_urls += [url]

    update_letter_table_by_urls(letter_urls)


def update_companies_group_letters(query: CodalQuery, group_code: str):
    print("\033[93m", "Warning: Sure that stock table in database must be updated!", "\033[0m")
    print("Note: If database is not updated, You can run the fill_stocks_table function first!")
    stocks = session.query(Stocks.symbol).filter_by(group_code=group_code).all()
    print(f"Letters group: {group_code} Started.")
    symbols = [stock[0] for stock in stocks]
    update_letters_table(query, symbols)
    print(f"Letters group: {group_code} Finished.")


def fill_letters_table(query: CodalQuery):
    start_time = time()
    print("\033[93m", "Warning: Sure that stock table in database must be updated!", "\033[0m")
    print("Note: If database is not updated, You can run the fill_stocks_table function first!")
    codes = session.query(Stocks.group_code).distinct().all()
    for i, code in enumerate(codes):
        print(f"Total progress: {100 * (i + 1) / len(codes):.2f}%")
        update_companies_group_letters(query, code[0])

    print("All letters Finished.", " " * 50)
    print(f"Time: {time() - start_time:.f} s")
