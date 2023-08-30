import sys
import asyncio
import aiohttp

import codal_tsetmc.config as db
from codal_tsetmc.tools import *
from codal_tsetmc.download.codal.query import CodalQuery
from codal_tsetmc.models import Companies

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
    df["CompanySymbol"] = df["Symbol"]
    df = df[[
        "PublishDateTime", "SentDateTime", "TracingNo",
        "LetterSerial", "LetterCode", "LetterTypes", "LetterTitle",
        "CompanySymbol", "CompanyName",
    ]]
    df = df_col_to_snake_case(df)
    return df


async def get_letters_list_for_each_page_async(query, page = 1):
    try:
        headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        }
        query.set_page_number(page)
        url = query.get_query_url()
        async with aiohttp.ClientSession() as session:
            async with session.get(url, cookies={}, headers=headers, data="") as response:
                data = await response.json()
        
        if data["Page"] == 1:
            df = convert_letter_list_to_df(data["Letters"])
            fill_table_of_db_with_df(df, "letters", "tracing_no")
        
        if query.pages is None:
            query.pages = data["Page"]
            return True
        else:
            df = convert_letter_list_to_df(data["Letters"])
            fill_table_of_db_with_df(df, "letters", "tracing_no")
        
        return True
    
    except Exception as e:
        return e

def update_letters_table_by_query_async(query, msg=""):
    if sys.platform == 'win32' or sys.platform == 'win64':
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.get_event_loop()
    
    try:
        tasks = [get_letters_list_for_each_page_async(query)]

        while query.pages is None:
            results = loop.run_until_complete(asyncio.gather(*tasks))

        if query.pages > 1:
            reversed_range = list(range(1, query.pages + 1))
            tasks = [get_letters_list_for_each_page_async(query, page=page) for page in reversed_range]
            results = loop.run_until_complete(asyncio.gather(*tasks))
        
        return results
    
    except RuntimeError:
        WARNING_COLOR = "\033[93m"
        ENDING_COLOR = "\033[0m"
        print(
            f"{WARNING_COLOR}If you are using jupyter notebook, please run following command:{ENDING_COLOR}"
        )
        print("```")
        print("%pip install nest_asyncio")
        print("import nest_asyncio; nest_asyncio.apply()")
        print("```")
        raise RuntimeError


def update_company_information_and_interim_financial_statements_letters(symbol, from_date="1350/01/01"):
    query = CodalQuery()
    query.set_symbol(symbol)
    query.set_category('اطلاعات و صورت مالی سالانه')
    query.set_letter_type('اطلاعات و صورتهای مالی میاندوره ای')
    q = f"SELECT max(publish_date_time) AS date FROM letters WHERE company_symbol = '{symbol}' AND letter_code = 'ن-10'"
    max_date = pd.read_sql(q, db.engine)
    
    if max_date.date.iat[0] is None:    
        query.set_from_date(from_date)
    else:
        last_date = num_to_datetime(max_date.date.iat[0], datetime = False)

        if last_date > from_date:
            query.set_from_date(last_date)
        else:
            query.set_from_date(from_date)

    results = update_letters_table_by_query_async(query)
    return results


def update_company_monthly_performance_report_letters(symbol, from_date="1350/01/01"):
    query = CodalQuery()
    query.set_symbol(symbol)
    query.set_category('گزارش عملکرد ماهانه')
    query.set_letter_type('گزارش فعالیت ماهانه')
    q = f"SELECT max(publish_date_time) AS date FROM letters WHERE company_symbol = '{symbol}' AND (letter_code = 'ن-30' OR letter_code = 'ن-31')"
    max_date = pd.read_sql(q, db.engine)
    
    if max_date.date.iat[0] is None:    
        query.set_from_date(from_date)
    else:
        last_date = num_to_datetime(max_date.date.iat[0], datetime = False)
        
        if last_date > from_date:
            query.set_from_date(last_date)
        else:
            query.set_from_date(from_date)


    results = update_letters_table_by_query_async(query)
    return results



def fill_bourse_and_fara_companies_letters():
    bors = db.session.query(db.distinct(Companies.symbol)).filter_by(status_code = 0)
    fara = db.session.query(db.distinct(Companies.symbol)).filter_by(status_code = 1)
    symbols = [symbol[0].strip() for symbol in bors] + [symbol[0].strip() for symbol in fara]
    
    for i, symbol in enumerate(symbols):
        print(
            f"total progress: {100*(i+1)/len(symbols):.2f}%",
            end="\n"
        )
        update_company_information_and_interim_financial_statements_letters(symbol)
        # update_company_monthly_performance_report_letters(symbol)
    
    print("letters Download Finished.", " "*50)

