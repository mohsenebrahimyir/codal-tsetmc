import requests
import re
import asyncio
import aiohttp
import codal_tsetmc.config as db
from codal_tsetmc.models import Stocks
from codal_tsetmc.tools import *
from jdatetime import datetime as jdatetime

from codal_tsetmc.models import (
    CompanyStatuses, CompanyTypes, Companies,
    ReportTypes, LetterTypes, Auditors, Letters
)

"""################
گرفتن اطلاعات از کدال 
################"""

# گرفتن اطلاعات کلی در یک صفحه
def get_api_sigle_page(query) -> dict:
    url = query.get_api_search_url()
    response = get_dict_from_xml_api(url)
    query.total = response["Total"]
    query.page = response["Page"]
    
    return response["Letters"]


# گرفتن اطلاعات کلی در همه صفحات
def get_api_multi_page(query, pages: int = 0) -> dict:
    last_letters = get_api_sigle_page(query)
    letters = []
    pages = pages if bool(pages) else query.page
    reversed_range = list(range(2, pages + 1))
    reversed_range.sort(reverse=True)
    for page in reversed_range:
        print(f"get page {page} of {pages}", end="\r", flush=True)
        query.set_page_number(page)
        letters += get_api_sigle_page(query)
    
    letters += last_letters

    return letters


# گرفتن اطلاعات کلی تمام صفحات به صورت یک فرمت داده
def get_letters(query, pages: int = 0, show = False) -> pd.DataFrame:
    letters = query.get_api_multi_page(pages)
    df = pd.DataFrame(letters).replace(regex=FA_TO_EN_DIGITS)
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

"""##########################
آپدیت کردن گزارشات در دیتابیس
##########################"""

# آپدیت کردن دیتابیس
def update_letters(query):
    try:
        df = query.get_letters(show=True)
        fill_table_of_db_with_df(df, "letters", "tracing_no")
        return True
    except Exception as e:
        return e

def update_company_letters(query):
    try:
        now = jdatetime.now().strftime("%Y%m%d%H%M%S")
        try:
            symbol = query.params["Symbol"]
            max_date_query = (
                f"select max(publish_date_time) as date from letters where company_symbol = '{symbol}'"
            )
            max_date = pd.read_sql(max_date_query, db.engine)
            last_date = max_date.date.iat[0]
        except Exception as e:
            last_date = None
        
        try:
            if last_date is None:  # no any record added in database
                query.set_from_date("1301/01/01")
            elif str(last_date) < now:  # need to updata new data
                query.set_from_date(num_to_datetime(last_date, datetime=False))
            else:  # The data for this symbol is updateed
                return
        
        except Exception as e:
            print(f"Error on formating:{str(e)}")
            
        query.update_letters()
    
    except Exception as e:
        return e, symbol

def update_companies_letters(query):
    len_symbols = len(query.symbols)
    for i, symbol in enumerate(query.symbols):
        print(f"{' '*18} total progress: {100*(i+1)/len_symbols:.2f}% {symbol}", end="\r", flush=True)
        query.set_symbol(symbol)
        query.update_company_letters()

def update_companies_status_letters(query, status):
    code = CompanyStatuses.query.filter_by(title=status).first().code
    companies = db.session.query(Companies.symbol).filter_by(status_code=0).all()
    query.symbols = [company[0] for company in companies]
    query.update_companies_letters()

def update_bourse_companies_letters(query):
    query.update_companies_status_letters("پذیرفته شده در بورس تهران")

def update_farabourse_companies_letters(query):
    query.update_companies_status_letters("پذیرفته شده در فرابورس ایران")
