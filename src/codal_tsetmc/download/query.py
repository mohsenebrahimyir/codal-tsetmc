import pandas as pd
import urllib.parse as urlparse
from urllib.parse import urlencode
from jdatetime import datetime as jdatetime

import codal_tsetmc.config as db
from codal_tsetmc.tools import *
from codal_tsetmc.models import (
    CompanyStatuses, CompanyTypes, Companies,
    ReportTypes, LetterTypes, Auditors, Letters
)


class CodalQuery:

    def __init__(self):
        # جستوجی اطاعیه‌های سایت کودال
        self.base_url = "codal.ir"
        self.report_list_html = f"https://{self.base_url}/ReportList.aspx?"
        self.search_query_xml = f"https://search.{self.base_url}/api/search/v2/q?"
        self.params = {
            "PageNumber": 1,
            "Symbol": -1,
            "PublisherStatus": -1,
            "Category": -1,
            "CompanyType": -1,
            "LetterType": -1,
            "Subject": -1,
            "TracingNo": -1,
            "LetterCode": -1,
            "Lenght": -1,
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

    # تنظیم لیست گزارش
    def get_report_list_url(self) -> str:
        return self.get_query_url(False)

    # تنظیم کوئری جستوجو
    def get_api_search_url(self) -> str:
        return self.get_query_url(True)

    # تنظیم شماره صفحه
    def set_page_number(self, number: int = None) -> None:
        if bool(number):
            BadValueInput(number).integer_type()
            self.params['PageNumber'] = number
        else:
            self.params['PageNumber'] += 1

    # تنظیم نام نماد
    def set_symbol(self, symbol: str = None) -> None:
        BadValueInput(symbol).string_type()
        symbol = Companies.query.filter_by(symbol=symbol).first().symbol
        self.params['Symbol'] = symbol if bool(symbol) else -1

    # تنظیم شماره ISIC
    def set_isic(self, isic: str = "") -> None:
        BadValueInput(isic).string_type()
        self.params['Isic'] = -1 if isic == "" else isic

    # تنظیم وضعیت ناشز
    def set_publisher_status(self, title: str = None) -> None:
        BadValueInput(title).string_type()
        code = CompanyStatuses.query.filter_by(title=title).first()
        self.params['PublisherStatus'] = code.code if bool(code) else -1

    # تنظیم گروع اطلاعیه
    def set_category(self, title: str = None) -> None:
        BadValueInput(title).string_type()
        code = ReportTypes.query.filter_by(title=title).first()
        self.params["Category"] = code.code if bool(code) else -1

    # تنظیم نوع شرکت
    def set_company_type(self, title: str = "") -> None:
        BadValueInput(title).string_type()
        code = CompanyTypes.query.filter_by(title=title).first()
        self.params["CompanyType"] = code.code if bool(code) else -1

    # تنظیم نوع اطلاعیه
    def set_letter_type(self, title: str = "") -> None:
        BadValueInput(title).string_type()
        code = LetterTypes.query.filter_by(title=title).first()
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
        lengthPeriod = {
            None: -1,
            'همه موارد': -1,
            '-۱': -1, '۰': -1,
            '۱': 1, '۲': 2, '۳': 3, '۴': 4, '۵': 5, '۶': 6,
            '۷': 7, '۸': 8, '۹': 9, '۱۰': 10, '۱۱': 11, '۱۲': 12,
            -1: -1, 0: -1,
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
            7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12
        }
        self.params["Length"] = -1 if period == "" else lengthPeriod[period]

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
        BadValueInput(status).boolian_type()
        self.params["Audited"] = str(status).lower()

    # تنظیم حسابرسی نشده
    def set_not_audited(self, status: bool = True) -> None:
        BadValueInput(status).boolian_type()
        self.params["NotAudited"] = str(status).lower()

    # تنظیم اصلی
    def set_consolidatable(self, status: bool = True) -> None:
        BadValueInput(status).boolian_type()
        self.params["Consolidatable"] = str(status).lower()

    # تنظیم تلفیقی
    def set_not_consolidatable(self, status: bool = True) -> None:
        BadValueInput(status).boolian_type()
        self.params["NotConsolidatable"] = str(status).lower()

    # تنظیم فقط زیرمجموعه ها
    def set_childs(self, status: bool = True) -> None:
        BadValueInput(status).boolian_type()
        self.params["Childs"] = str(status).lower()

    # تنظیم فقط شرکت اصلی
    def set_mains(self, status: bool = True) -> None:
        BadValueInput(status).boolian_type()
        self.params["Mains"] = str(status).lower()

    # تنظیم موسسه حسابرسی شرکت
    def set_auditor_ref(self, name: str = None) -> None:
        BadValueInput(name).string_type()
        code = Auditors.query.filter_by(name=name).first()
        self.params["AuditorRef"] = code.code if bool(code) else -1

    # سالی مالی منتهی به
    def set_year_end_to_date(self, date: str = "1300/01/01") -> None:
        BadValueInput(date).date_type()
        self.params["YearEndToDate"] = -1 if date == "" else date

    # تنظیم فقط اطلاعیه های منتشر شده از طرف سازمان
    def set_publisher(self, status: bool = True) -> None:
        BadValueInput(status).boolian_type()
        self.params["Publisher"] = str(status).lower()
    
    # حذف تنظیمات
    def remove_none(self, dictionary) -> dict:
        filtered = {k: v for k, v in dictionary.items() if v != -1}
        dictionary.clear()
        dictionary.update(filtered)
        return dictionary
    
    """################
    گرفتن اطلاعات از کدال 
    ################"""

    # گرفتن لینک
    def get_query_url(self, api: bool = True) -> str:
        params = self.params
        BadValueInput(api).boolian_type()
        url = self.search_query_xml if api else self.report_list_html
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(self.remove_none(params))
        url_parts[4] = f"&{urlencode(query)}&search=true" if api else f"search&{urlencode(query)}"

        return urlparse.urlunparse(url_parts)

    # گرفتن اطلاعات کلی در یک صفحه
    def get_api_sigle_page(self) -> dict:
        url = self.get_api_search_url()
        response = get_dict_from_xml_api(url)
        self.total = response["Total"]
        self.page = response["Page"]
        
        return response["Letters"]

    # گرفتن اطلاعات کلی در همه صفحات
    def get_api_multi_page(self, pages: int = 0) -> dict:
        last_letters = self.get_api_sigle_page()
        letters = []
        pages = pages if bool(pages) else self.page
        reversed_range = list(range(2, pages + 1))
        reversed_range.sort(reverse=True)
        for page in reversed_range:
            
            print(f"get page {page} of {pages}", end="\r", flush=True)

            self.set_page_number(page)
            letters += self.get_api_sigle_page()
        
        letters += last_letters

        return letters

    # گرفتن اطلاعات کلی تمام صفحات به صورت یک فرمت داده
    def get_letters(self, pages: int = 0, show = False) -> pd.DataFrame:
        letters = self.get_api_multi_page(pages)
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
        if show:
            return df
        else:
            self.letters = df
    
    """##########################
    آپدیت کردن گزارشات در دیتابیس
    ##########################"""

    # آپدیت کردن دیتابیس
    def update_letters(self):
        try:
            df = self.get_letters(show=True)
            fill_table_of_db_with_df(df, "letters", "tracing_no")
            return True
        except Exception as e:
            return e

    def update_company_letters(self):
        try:
            now = jdatetime.now().strftime("%Y%m%d%H%M%S")
            try:
                symbol = self.params["Symbol"]
                max_date_query = (
                    f"select max(publish_date_time) as date from letters where company_symbol = '{symbol}'"
                )
                max_date = pd.read_sql(max_date_query, db.engine)
                last_date = max_date.date.iat[0]
            except Exception as e:
                last_date = None
            
            try:
                if last_date is None:  # no any record added in database
                    self.set_from_date("1301/01/01")
                elif str(last_date) < now:  # need to updata new data
                    self.set_from_date(num_to_datetime(last_date, datetime=False))
                else:  # The data for this symbol is updateed
                    return
            
            except Exception as e:
                print(f"Error on formating:{str(e)}")
                
            self.update_letters()
        
        except Exception as e:
            return e, symbol

    def update_companies_letters(self):
        len_symbols = len(self.symbols)
        for i, symbol in enumerate(self.symbols):
            print(f"{' '*18} total progress: {100*(i+1)/len_symbols:.2f}% {symbol}", end="\r", flush=True)
            self.set_symbol(symbol)
            self.update_company_letters()

    def update_companies_status_letters(self, status):
        code = CompanyStatuses.query.filter_by(title=status).first().code
        companies = db.session.query(Companies.symbol).filter_by(status_code=0).all()
        self.symbols = [company[0] for company in companies]
        self.update_companies_letters()

    def update_bourse_companies_letters(self):
        self.update_companies_status_letters("پذیرفته شده در بورس تهران")

    def update_farabourse_companies_letters(self):
        self.update_companies_status_letters("پذیرفته شده در فرابورس ایران")


class Categories:

    def __init__(self) -> None:
        self.url = 'https://search.codal.ir/api/search/v1/'

    def get_data(self):
        # TODO: ...
        """_summary_
        Returns:
            _type_: _description_
        """

        api = get_dict_from_xml_api(self.url + "categories")
        report_types = []
        company_types = []
        letter_types = []
        categories = []

        for item in api:
            publisher_types_items = item.pop("PublisherTypes")
            if item["Code"] != -1:
                for publisher_type in publisher_types_items:
                    letter_types_items = publisher_type.pop("LetterTypes")
                    for letter_type in letter_types_items:
                        if letter_type not in letter_types:
                            letter_types += [{
                                "code": letter_type["Id"],
                                "title": letter_type["Name"]
                            }]
                        categories += [{
                            "report_types_code": pd.to_numeric(item["Code"]),
                            "company_types_code": pd.to_numeric(publisher_type["Code"]),
                            "letter_type_code": pd.to_numeric(letter_type["Id"]),
                        }]
            else:
                for publisher_type in publisher_types_items:
                    company_types += [{
                        "code": pd.to_numeric(publisher_type["Code"]),
                        "title": publisher_type["Name"]
                    }]

            report_types += [{"code": item["Code"], "title": item["Name"]}]

        self.report_types = pd.DataFrame(report_types) \
            .sort_values("code").reset_index(drop=True)
        self.company_types = pd.DataFrame(company_types) \
            .sort_values("code").reset_index(drop=True)
        self.letter_types = pd.DataFrame(letter_types) \
            .drop_duplicates().sort_values("code").reset_index(drop=True)
        self.categories = pd.DataFrame(categories) \
            .drop_duplicates().reset_index(drop=True)
        self.company_statuses = pd.DataFrame({
            "code": [-1, 0, 1, 2, 3, 4, 5],
            "title": [
                'همه موارد',
                'پذیرفته شده در بورس تهران',
                'پذیرفته شده در فرابورس ایران',
                'ثبت شده پذیرفته نشده',
                'ثبت نشده نزد سازمان',
                'پذیرفته شده در بورس کالای ایران',
                'پذیرفته شده دربورس انرژی ایران'
            ]
        }).sort_values("code").reset_index(drop=True)

        api = get_dict_from_xml_api(self.url + "auditors")
        self.auditors = pd.DataFrame(api)
        self.auditors.columns = ["name", "code"]
        self.auditors.sort_values("code").reset_index(drop=True, inplace=True)

        api = get_dict_from_xml_api(self.url + "financialYears")
        self.financial_years = pd.DataFrame(api)
        self.financial_years.columns = ["date"]

    def fill_categories_table(self):
        self.get_data()
        fill_table_of_db_with_df(
            self.company_statuses, "company_statuses", "code"
        )
        fill_table_of_db_with_df(self.report_types, "report_types", "code")
        fill_table_of_db_with_df(self.company_types, "company_types", "code")
        fill_table_of_db_with_df(self.letter_types, "letter_types", "code")
        fill_table_of_db_with_df(self.auditors, "auditors", "code")
        fill_table_of_db_with_df(self.financial_years, "financial_years", "date")



if __name__ == '__main__':
    pass
