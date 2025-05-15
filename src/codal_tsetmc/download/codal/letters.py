import sys
import asyncio
from time import time

import aiohttp
import nest_asyncio
import pandas as pd

from codal_tsetmc.config.engine import session
from codal_tsetmc.models import Stock, Letter
from codal_tsetmc.tools.api import GET_HEADERS_REQUEST
from codal_tsetmc.tools.string import (
    FA_TO_EN_DIGITS,
    datetime_to_num, df_col_to_snake_case,
)

from codal_tsetmc.tools.database import (
    fill_table_of_db_with_df,
    create_table_if_not_exist
)
from codal_tsetmc.download.codal.query import CodalQuery

"""################
گرفتن اطلاعات از کدال
################"""

LETTERS_CODE_TO_TYPE = {
    "ن-10": "اطلاعات و صورتهای مالی میاندوره ای",
    "ن-11": "گزارش فعالیت هیئت مدیره",
    "ن-12": "گزارش کنترل های داخلی",
    "ن-13": "زمانبندی پرداخت سود",
    "ن-20": "افشای اطلاعات با اهمیت",
    "ن-21": "شفاف سازی در خصوص شایعه، خبر یا گزارش منتشر شده",
    "ن-22": "شفاف سازی در خصوص نوسان قیمت سهام",
    "ن-23": "اطلاعات حاصل از برگزاری کنفرانس اطلاع رسانی",
    "ن-24": "درخواست ارایه مهلت جهت رعایت ماده  19 مکرر 1/ 12 مکرر 4 دستورالعمل اجرایی نحوه انجام معاملات",
    "ن-25": "برنامه ناشر جهت خروج از شمولیت ماده 141 لایحه قانونی اصلاحی قسمتی از قانون تجارت",
    "ن-26": "توضیحات در خصوص اطلاعات و صورت های مالی منتشر شده",
    "ن-30": "گزارش فعالیت ماهانه",
    "ن-41": "مشخصات کمیته حسابرسی و واحد حسابرسی داخلی",
    "ن-42": "آگهی ثبت تصمیمات مجمع عادی سالیانه",
    "ن-43": "اساسنامه شرکت مصوب مجمع عمومی فوق العاده",
    "ن-45": "معرفی یا تغییر در ترکیب اعضای هیئت‌مدیره",
    "ن-50": "آگهی دعوت به مجمع عمومی عادی سالیانه",
    "ن-51": "خلاصه تصمیمات مجمع عمومی عادی سالیانه",
    "ن-52": "تصمیمات مجمع عمومی عادی سالیانه",
    "ن-53": "آگهی دعوت به مجمع عمومی عادی سالیانه نوبت دوم",
    "ن-54": "آگهی دعوت به مجمع عمومی عادی بطور فوق العاده",
    "ن-55": "تصمیمات مجمع عمومی عادی به‌طور فوق‌العاده",
    "ن-56": "آگهی دعوت به مجمع عمومی فوق العاده",
    "ن-57": "تصمیمات مجمع عمومی فوق‌العاده",
    "ن-58": "لغو  آگهی (اطلاعیه) دعوت به مجمع عمومی",
    "ن-59": "مجوز بانک مرکزی جهت برگزاری مجمع عمومی عادی سالیانه",
    "ن-60": "پیشنهاد هیئت مدیره به مجمع عمومی فوق العاده در خصوص افزایش سرمایه",
    "ن-61": "اظهارنظر حسابرس و بازرس قانونی نسبت به گزارش توجیهی هیئت مدیره در خصوص افزایش سرمایه",
    "ن-62": "مدارک و مستندات درخواست افزایش سرمایه",
    "ن-63": "تمدید مهلت استفاده از مجوز افزایش سرمایه",
    "ن-64": "مهلت استفاده از حق تقدم خرید سهام",
    "ن-65": "اعلامیه پذیره نویسی عمومی",
    "ن-66": "نتایج حاصل از فروش حق تقدم های استفاده نشده",
    "ن-67": "آگهی ثبت افزایش سرمایه",
    "ن-69": "توزیع گواهی نامه نقل و انتقال و سپرده سهام",
    "ن-70": "تصمیم هیئت مدیره به انجام افزایش سرمایه تفویض شده در مجمع فوق العاده",
    "ن-71": "زمان تشکیل جلسه هیئت‌مدیره در خصوص افزایش سرمایه",
    "ن-72": "لغو اطلاعیه زمان تشکیل جلسه هیات مدیره در خصوص افزایش سرمایه",
    "ن-73": "تصمیمات هیئت‌مدیره در خصوص افزایش سرمایه",
    "ن-80": "تغییر نشانی",
    "ن-81": "درخواست تکمیل مشخصات سهامداران",
}

LETTERS_TYPE_TO_CODE = {y: x for x, y in LETTERS_CODE_TO_TYPE.items()}


def convert_letter_list_to_df(data) -> pd.DataFrame:
    df = pd.DataFrame(data).replace(regex=FA_TO_EN_DIGITS)
    df["Serial"] = df["Url"].replace(regex={
        r"^.*LetterSerial=": "",
        r"\&.*$": ""
    })
    df["Code"] = df["LetterCode"]
    df["Type"] = df["LetterCode"].replace(regex=LETTERS_CODE_TO_TYPE)
    df["PublishDateTime"] = df["PublishDateTime"].apply(datetime_to_num)
    df["SentDateTime"] = df["SentDateTime"].apply(datetime_to_num)
    df = df[[
        "PublishDateTime", "SentDateTime", "TracingNo",
        "Serial", "Title", "Code", "Type", "Symbol", "CompanyName",
        "HasHtml", "HasAttachment", "HasPdf", "HasXbrl", "HasExcel"
    ]]
    df = df_col_to_snake_case(df)

    return df


async def get_letters_urls_from_page_100000_async(ses, url: str):
    nest_asyncio.apply()

    async with ses.get(url, cookies={}, headers=GET_HEADERS_REQUEST,
                       data="") as response:
        data = await response.json()

    u = url.split("100000")
    return [f'{u[0]}{data["Page"] + 1 - i}{u[1]}' for i in
            range(1, data["Page"] + 1)]


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
        async with ses.get(url, cookies={}, headers=GET_HEADERS_REQUEST,
                           data="") as response:
            data = await response.json()

        df = convert_letter_list_to_df(data["Letters"])

        model = Letter
        create_table_if_not_exist(model)
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

        _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
            _ProactorBasePipeTransport.__del__)

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
    print("\033[93m",
          "Warning: Sure that stock table in database must be updated!",
          "\033[0m")
    print(
        "Note: If database is not updated, You can run the fill_stocks_table function first!")
    stocks = session.query(Stock.symbol).filter_by(group_code=group_code).all()
    print(f"Letters group: {group_code} Started.")
    symbols = [stock[0] for stock in stocks]
    update_letters_table(query, symbols)
    print(f"Letters group: {group_code} Finished.")


def fill_letters_table(query: CodalQuery):
    start_time = time()
    print("\033[93m",
          "Warning: Sure that stock table in database must be updated!",
          "\033[0m")
    print(
        "Note: If database is not updated, You can run the fill_stocks_table function first!")
    codes = session.query(Stock.group_code).distinct().all()
    for i, code in enumerate(codes):
        print(f"Total progress: {100 * (i + 1) / len(codes):.2f}%")
        update_companies_group_letters(query, code[0])

    print("All letters Finished.", " " * 50)
    print(f"Time: {time() - start_time:.f} s")
