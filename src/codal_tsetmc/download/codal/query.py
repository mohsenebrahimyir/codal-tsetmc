from typing import Any

import pandas as pd
import urllib.parse as urlparse
from urllib.parse import urlencode

from codal_tsetmc.tools.exception import *
from codal_tsetmc.tools.string import (
    FA_TO_EN_DIGITS, df_col_to_snake_case, datetime_to_num
)
from codal_tsetmc.tools.api import get_dict_from_xml_api
from codal_tsetmc.models import (
    CompanyState, CompanyType, Company, IndustryGroup,
    LetterGroup, LetterType, Auditor, ReportingType
)


def remove_none(dictionary) -> dict:
    filtered = {k: v for k, v in dictionary.items() if v != -1}
    dictionary.clear()
    dictionary.update(filtered)

    return dictionary


class CodalQuery:

    def __init__(self):
        # جستجوی اطاعیه‌های سایت کودال
        self.page = None
        self.total = None
        self.letters = None
        self.base_url = "codal.ir"
        self.report_list_html = f"https://{self.base_url}/ReportList.aspx?"
        self.search_query_xml = f"https://search.{self.base_url}/api/search/v2/q?"
        self.pages = None
        self.params = {
            "PageNumber": 1,
            "Symbol": -1,
            "name": -1,
            "ReportingType": -1,
            "CompanyType": -1,
            "IndustryGroup": -1,
            "CompanyState": -1,
            "LetterType": -1,
            "Category": -1,
            "Subject": -1,
            "TracingNo": -1,
            "LetterCode": -1,
            "Length": -1,
            "FromDate": -1,
            "ToDate": -1,
            "Audited": "true",
            "NotAudited": "true",
            "Consolidatable": "true",
            "NotConsolidatable": "true",
            "Childs": "true",
            "Mains": "true",
            "AuditorRef": -1,
            "YearEndToDate": -1,
            "Publisher": "false",
        }

    """###################
    تنظیمات لازم برای کوئری
    ###################"""

    # تنظیم نام نماد
    def set_symbol(self, symbol: str = "") -> None:
        BadValueInput(symbol).string_type()
        self.params['Symbol'] = symbol if bool(symbol) else -1

    # تنظیم نام نماد
    def set_name(self, name: str = "") -> None:
        BadValueInput(name).string_type()
        self.params['name'] = name if bool(name) else -1

    # تنظیم شماره ISIC
    def set_isic(self, isic: str = "") -> None:
        BadValueInput(isic).string_type()
        self.params['Isic'] = -1 if isic == "" else isic

    # تنظیم وضعیت ناشر
    def set_publisher_status(self, title: str = "") -> None:
        BadValueInput(title).string_type()
        code = CompanyState.query.filter_by(title=title).first()
        self.params['CompanyState'] = code.code if bool(code) else -1

    # تنظیم گروع اطلاعیه
    def set_category(self, title: str = "") -> None:
        BadValueInput(title).string_type()
        code = LetterGroup.query.filter_by(title=title).first()
        self.params["Category"] = code.code if bool(code) else -1

    # تنظیم نوع شرکت
    def set_company_type(self, title: str = "") -> None:
        BadValueInput(title).string_type()
        code = CompanyType.query.filter_by(title=title).first()
        self.params["CompanyType"] = code.code if bool(code) else -1  # تنظیم نوع شرکت

    # تنظیم نوع صنعت
    def set_industry_group(self, name: str = "") -> None:
        BadValueInput(name).string_type()
        code = IndustryGroup.query.filter_by(name=name).first()
        self.params["IndustryGroup"] = code.code if bool(code) else -1

    # تنظیم نوع اطلاعیه
    def set_letter_type(self, title: str = "") -> None:
        BadValueInput(title).string_type()
        code = LetterType.query.filter_by(title=title).first()
        self.params["LetterType"] = code.code if bool(code) else -1

    # تنظیم موضوع اطلاعیه
    def set_subject(self, subject: str = "") -> None:
        BadValueInput(subject).string_type()
        self.params["Subject"] = -1 if subject == "" else subject

    # تنظیم شماره پیگیری
    def set_tracing_no(self, no: str = "") -> None:
        BadValueInput(no).int_str_type()
        self.params["TracingNo"] = -1 if no == "" else no

    # تنظیم کد اطلاعیه
    def set_letter_code(self, code: str = "") -> None:
        BadValueInput(code).int_str_type()
        self.params["LetterCode"] = -1 if code == "" else code

    # تنظیم طول دوره
    def set_length_period(self, period=-1) -> None:
        # طول دوره
        length_period = {
            None: -1, 'همه موارد': -1, '-۱': -1, '۰': -1,
            '۱': 1, '۲': 2, '۳': 3, '۴': 4, '۵': 5, '۶': 6,
            '۷': 7, '۸': 8, '۹': 9, '۱۰': 10, '۱۱': 11, '۱۲': 12,
            -1: -1, 0: -1,
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
            7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12
        }
        self.params["Length"] = -1 if period == "" else length_period[period]

    # تنظیم از تاریخ
    def set_from_date(self, date: str = "1300/01/01") -> None:
        BadValueInput(date).date_type()
        self.params["FromDate"] = -1 if date == "" else date

    # تنظیم تا تاریخ
    def set_to_date(self, date: str = "1500/01/01") -> None:
        BadValueInput(date).date_type()
        self.params["ToDate"] = -1 if date == "" else date

    # تنظیم حسابرسی شده
    def set_audited(self, status: bool = True) -> None:
        BadValueInput(status).boolean_type()
        self.params["Audited"] = str(status).lower()

    # تنظیم حسابرسی نشده
    def set_not_audited(self, status: bool = True) -> None:
        BadValueInput(status).boolean_type()
        self.params["NotAudited"] = str(status).lower()

    # تنظیم اصلی
    def set_consolidate_table(self, status: bool = True) -> None:
        BadValueInput(status).boolean_type()
        self.params["Consolidatable"] = str(status).lower()

    # تنظیم تلفیقی
    def set_not_consolidate_table(self, status: bool = True) -> None:
        BadValueInput(status).boolean_type()
        self.params["NotConsolidatable"] = str(status).lower()

    # تنظیم فقط زیرمجموعه ها
    def set_childs(self, status: bool = True) -> None:
        BadValueInput(status).boolean_type()
        self.params["Childs"] = str(status).lower()

    # تنظیم فقط شرکت اصلی
    def set_mains(self, status: bool = True) -> None:
        BadValueInput(status).boolean_type()
        self.params["Mains"] = str(status).lower()

    # تنظیم موسسه حسابرسی شرکت
    def set_auditor_ref(self, name: str = None) -> None:
        BadValueInput(name).string_type()
        code = Auditor.query.filter_by(name=name).first()
        self.params["AuditorRef"] = code.code if bool(code) else -1

    # سالی مالی منتهی به
    def set_year_end_to_date(self, date: str = "1300/01/01") -> None:
        BadValueInput(date).date_type()
        self.params["YearEndToDate"] = -1 if date == "" else date

    # تنظیم فقط اطلاعیه های منتشر شده از طرف سازمان
    def set_publisher(self, status: bool = True) -> None:
        BadValueInput(status).boolean_type()
        self.params["Publisher"] = str(status).lower()

    # حذف تنظیمات

    # تنظیم شماره صفحه
    def set_page_number(self, number: int = 0) -> None:
        if bool(number):
            BadValueInput(number).integer_type()
            self.params['PageNumber'] = number
        else:
            self.params['PageNumber'] += 1

    def get_page_number(self) -> int:
        return self.params['PageNumber']

    def set_pages_number(self, number: int = 0) -> None:
        if bool(number):
            BadValueInput(number).integer_type()
            self.pages = number

    """################
    گرفتن لینک کوئری کدال 
    ################"""

    # گرفتن لینک
    def get_query_url(self, api: bool = True) -> str:
        params = self.params
        BadValueInput(api).boolean_type()
        url = self.search_query_xml if api else self.report_list_html
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(remove_none(params))
        url_parts[4] = f"&{urlencode(query)}&search=true" if api else f"search&{urlencode(query)}"

        return urlparse.urlunparse(url_parts)

    # گرفتن لیست گزارش
    def get_report_list_url(self) -> str:
        return self.get_query_url(False)

    # گرفتن کوئری جستوجو
    def get_api_search_url(self) -> str:
        return self.get_query_url(True)

    """################
    گرفتن اطلاعات از کدال 
    ################"""

    # گرفتن اطلاعات کلی در یک صفحه
    def get_api_single_page(self) -> dict:
        url = self.get_api_search_url()
        response = get_dict_from_xml_api(url)
        self.total = response["Total"]
        self.page = response["Page"]

        return response["Letters"]

    # گرفتن اطلاعات کلی در همه صفحات
    def get_api_multi_page(self, pages: int = 0) -> list[Any]:
        last_letters = self.get_api_single_page()
        letters = []
        pages = pages if bool(pages) else self.page
        reversed_range = list(range(2, pages + 1))
        reversed_range.sort(reverse=True)
        for page in reversed_range:
            print(f"get page {page} of {pages}")
            self.set_page_number(page)
            letters += self.get_api_single_page()

        letters += last_letters

        return letters

    # گرفتن اطلاعات کلی تمام صفحات به صورت یک فرمت داده
    def get_letters(self, pages: int = 0, show=False) -> pd.DataFrame:
        letters = self.get_api_multi_page(pages)
        df = pd.DataFrame(letters).replace(regex=FA_TO_EN_DIGITS)
        df = df_col_to_snake_case(df)
        self.letters = df
        if show:
            return df
