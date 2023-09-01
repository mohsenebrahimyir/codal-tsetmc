import sys
import asyncio
import aiohttp
import pandas as pd

from codal_tsetmc.config.engine import session, engine
from codal_tsetmc.models.stocks import Stocks
from codal_tsetmc.tools.string import (
    FA_TO_EN_DIGITS, LETTERS_CODE_TO_TITLE, 
    datetime_to_num, df_col_to_snake_case, num_to_datetime,
)

from codal_tsetmc.tools.database import fill_table_of_db_with_df
from codal_tsetmc.tools.api import get_results_by_asyncio_loop
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
    df["LetterTypes"]     = df["LetterCode"].replace(regex=LETTERS_CODE_TO_TITLE)
    df["PublishDateTime"] = df["PublishDateTime"].apply(datetime_to_num)
    df["SentDateTime"]    = df["SentDateTime"].apply(datetime_to_num)
    df["LetterTitle"]     = df["Title"]
    df["Name"]            = df["CompanyName"]
    df = df[[
        "PublishDateTime", "SentDateTime", "TracingNo",
        "LetterSerial", "LetterCode", "LetterTypes", "LetterTitle",
        "Symbol", "Name",
    ]]
    df = df_col_to_snake_case(df)

    return df


async def get_letters_urls_from_page_100000_async(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    }
    async with session.get(url, cookies={}, headers=headers, data="") as response:
        data = await response.json()
    
    u = url.split("100000")
    return [f'{u[0]}{data["Page"] + 1 - i}{u[1]}' for i in range(1, data["Page"] + 1)]


async def get_letters_urls_async(urls):
    tasks = []
    results = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(get_letters_urls_from_page_100000_async(session, url))
        results = await asyncio.gather(*tasks)
    return results


def get_letter_urls_parallel(urls):

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    try:
        results = loop.run_until_complete(get_letters_urls_async(urls))

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
    
    return results


def get_letters_urls_by_symbols(query, symbols, msg=""):
    print(f"update letters urls ", end="\r")
    
    query.set_page_number(100000)
    urls = []
    
    for symbol in symbols:
        query.set_symbol(symbol)
        urls += [query.get_query_url()]
    
    results = get_letter_urls_parallel(urls)
    print(msg, end="\r")

    return results

async def update_letters_for_each_url_async(session, url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        }
        async with session.get(url, cookies={}, headers=headers, data="") as response:
            data = await response.json()

            df = convert_letter_list_to_df(data["Letters"])
            fill_table_of_db_with_df(df, "letters", "tracing_no")

            return True

    except Exception as e:
        return e


async def update_letters_for_urls_async(urls):
    tasks = []
    results = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(update_letters_for_each_url_async(session, url))
        results = await asyncio.gather(*tasks)

    return results


def update_letter_urls_parallel(urls):
    
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
        results = loop.run_until_complete(update_letters_for_urls_async(urls))

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
    
    finally:
        loop.close()
        return results
  



def update_letters_table_by_symbols(query, symbols, msg=""):
    print(f"update letters ", end="\r")
    urls_list = get_letters_urls_by_symbols(query, symbols)

    letter_urls = []
    for urls in urls_list:
        for url in urls:
            letter_urls += [url]
    
    results = update_letter_urls_parallel(letter_urls)
    return results


def update_companies_group_letters(query, group_code):
    stocks = session.query(Stocks.symbol).filter_by(group_code=group_code).all()
    print(f"{' '*25} group: {group_code}", end="\r")
    symbols = [stock[0] for stock in stocks]
    msg = "group "+group_code+" updated"
    results = update_letters_table_by_symbols(query, symbols, msg)
    return results


def fill_letters_table(query):
    codes = session.query(Stocks.group_code).distinct().all()
    for i, code in enumerate(codes):
        print(f"{' '*35} total progress: {100*(i+1)/len(codes):.2f}%", end="\r")
        update_companies_group_letters(query, code[0])
    
    print("letters Download Finished.", " "*50)


def fill_interim_financial_statements_letters(from_date = "1300/01/01", to_date = "1500/01/01"):
    query = CodalQuery()
    query.set_from_date(from_date)
    query.set_to_date(to_date)
    query.set_category('اطلاعات و صورت مالی سالانه')
    query.set_letter_type('اطلاعات و صورتهای مالی میاندوره ای')

    fill_letters_table(query)

def fill_symbols_interim_financial_statements_letters(symbols, from_date = "1300/01/01", to_date = "1500/01/01"):
    query = CodalQuery()
    query.set_from_date(from_date)
    query.set_to_date(to_date)
    query.set_category('اطلاعات و صورت مالی سالانه')
    query.set_letter_type('اطلاعات و صورتهای مالی میاندوره ای')

    results = update_letters_table_by_symbols(query, symbols)
    return results


def update_symbol_interim_financial_statements_letters(symbol, from_date = "1300/01/01", to_date = "1500/01/01"):
    query = CodalQuery()
    query.set_to_date(to_date)
    query.set_category('اطلاعات و صورت مالی سالانه')
    query.set_letter_type('اطلاعات و صورتهای مالی میاندوره ای')

    q = f"SELECT max(publish_date_time) AS date FROM letters WHERE symbol = '{symbol}' AND (letter_code = 'ن-30' OR letter_code = 'ن-31')"
    max_date = pd.read_sql(q, engine)
    
    if max_date.date.iat[0] is None:
        query.set_from_date(from_date)
    else:
        last_date = num_to_datetime(max_date.date.iat[0], datetime = False)
        
        if last_date > from_date:
            query.set_from_date(last_date)
        else:
            query.set_from_date(from_date)

    results = update_letters_table_by_symbols(query, [symbol])
    return results
