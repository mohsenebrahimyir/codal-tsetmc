import sys
import asyncio
import aiohttp
import nest_asyncio
import pandas as pd

from codal_tsetmc import Letters
from codal_tsetmc.config.engine import session, engine
from codal_tsetmc.models.stocks import Stocks
from codal_tsetmc.tools.string import (
    FA_TO_EN_DIGITS, LETTERS_CODE_TO_TITLE,
    datetime_to_num, df_col_to_snake_case, num_to_datetime,
)

from codal_tsetmc.tools.database import fill_table_of_db_with_df
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

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 '
                      'Safari/537.36',
    }
    async with ses.get(url, cookies={}, headers=headers, data="") as response:
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
        print("get_letter_urls_parallel: ", e.__context__, end="\r", flush=True)


def get_letters_urls_by_symbols(query: CodalQuery, symbols: list):
    query.set_page_number(100000)
    urls = []

    for symbol in symbols:
        query.set_symbol(symbol)
        urls += [query.get_query_url()]

    results = get_letter_urls_parallel(urls)

    return results


async def update_letters_for_each_url_async(ses, url: str):
    nest_asyncio.apply()

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 '
                          'Safari/537.36',
        }
        async with ses.get(url, cookies={}, headers=headers, data="") as response:
            data = await response.json()

            df = convert_letter_list_to_df(data["Letters"])

            try:
                Letters.__table__.create(engine)
            except Exception as e:
                print(e.__context__, end="\r", flush=True)

            fill_table_of_db_with_df(df, "letters", "tracing_no")

    except Exception as e:
        print("update_letters_for_each_url_async: ", e.__context__, end="\r", flush=True)


async def update_letters_for_urls_async(urls: list):
    nest_asyncio.apply()

    tasks = []
    async with aiohttp.ClientSession() as ses:
        for url in urls:
            tasks.append(update_letters_for_each_url_async(ses, url))
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
                except RuntimeError as e:
                    if str(e) != 'Event loop is closed':
                        raise

            return wrapper

        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)

        ##############################################################################
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(update_letters_for_urls_async(urls))
        loop.close()
    except Exception as e:
        print("update_letter_table_by_urls: ", e.__context__, end="\r", flush=True)


def update_letters_table_by_query_and_symbols(query: CodalQuery, symbols: list):
    urls_list = get_letters_urls_by_symbols(query, symbols)

    letter_urls = []
    for urls in urls_list:
        for url in urls:
            letter_urls += [url]

    update_letter_table_by_urls(letter_urls)


def update_companies_group_letters(query: CodalQuery, group_code: str):
    print("\033[93m", "Warning: Sure that stock table in database must be updated!", "\033[0m")
    print("Note: If database is not updated, You can run the fill_stocks_table function first!")
    stocks = session.query(Stocks.symbol).filter_by(group_code=group_code).all()
    print(f"{' ' * 25} group: {group_code}", end="\r")
    symbols = [stock[0] for stock in stocks]
    update_letters_table_by_query_and_symbols(query, symbols)
    print(f"letters group: {group_code} Finished.", " " * 50)


def fill_letters_table(query: CodalQuery):
    print("\033[93m", "Warning: Sure that stock table in database must be updated!", "\033[0m")
    print("Note: If database is not updated, You can run the fill_stocks_table function first!")
    codes = session.query(Stocks.group_code).distinct().all()
    for i, code in enumerate(codes):
        print(f"{' ' * 35} total progress: {100 * (i + 1) / len(codes):.2f}%", end="\r")
        update_companies_group_letters(query, code[0])

    print("All letters Finished.", " " * 50)

