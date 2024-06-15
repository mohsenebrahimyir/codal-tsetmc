import pandas as pd

from codal_tsetmc.models import (
    CompanyState, CompanyType, LetterType, ReportType, Auditor, FinancialYear
)
from codal_tsetmc.tools.api import get_dict_from_xml_api
from codal_tsetmc.tools.database import fill_table_of_db_with_df, create_table_if_not_exist
from codal_tsetmc.tools.string import datetime_to_num

models = [
    CompanyState, CompanyType,
    LetterType, ReportType,
    Auditor, FinancialYear,
]


class Categories:

    def __init__(self) -> None:
        self.url = 'https://search.codal.ir/api/search/v1/'
        self.result = {}

    def get_data(self):
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
                            "report_type_code": pd.to_numeric(item["Code"]),
                            "company_type_code": pd.to_numeric(publisher_type["Code"]),
                            "letter_type_code": pd.to_numeric(letter_type["Id"]),
                        }]
            else:
                for publisher_type in publisher_types_items:
                    company_types += [{
                        "code": pd.to_numeric(publisher_type["Code"]),
                        "title": publisher_type["Name"]
                    }]

            report_types += [{"code": item["Code"], "title": item["Name"]}]

        self.result["report_type"] = pd.DataFrame(report_types) \
            .sort_values("code").reset_index(drop=True)
        self.result["company_type"] = pd.DataFrame(company_types)
        self.result["company_type"].loc[-1] = [-1, "همه موارد"]
        self.result["company_type"] = self.result["company_type"].sort_values("code").reset_index(drop=True)

        self.result["letter_type"] = pd.DataFrame(letter_types) \
            .drop_duplicates().sort_values("code").reset_index(drop=True)
        self.result["category"] = pd.DataFrame(categories) \
            .drop_duplicates().reset_index(drop=True)
        self.result["company_state"] = pd.DataFrame({
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
        self.result["auditor"] = pd.DataFrame(api)
        self.result["auditor"].columns = ["name", "code"]
        self.result["auditor"].sort_values("code").reset_index(drop=True, inplace=True)

        api = get_dict_from_xml_api(self.url + "financialYears")
        self.result["financial_year"] = pd.DataFrame(api)
        self.result["financial_year"].columns = ["date"]
        self.result["financial_year"]["code"] = self.result["financial_year"]["date"].apply(datetime_to_num)

    def fill_categories_table(self):
        self.get_data()
        for model in models:
            tablename = model.__tablename__
            create_table_if_not_exist(model)
            fill_table_of_db_with_df(self.result[tablename], tablename, "code")


def fill_categories_table():
    cat = Categories()
    cat.fill_categories_table()


if __name__ == '__main__':
    pass
