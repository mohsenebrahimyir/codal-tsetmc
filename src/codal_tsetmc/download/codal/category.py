import pandas as pd

from codal_tsetmc import CompanyStatuses, CompanyTypes, LetterTypes
from codal_tsetmc.config.engine import engine
from codal_tsetmc.models.companies import ReportTypes, Auditors, FinancialYears
from codal_tsetmc.tools.api import get_dict_from_xml_api
from codal_tsetmc.tools.database import fill_table_of_db_with_df


class Categories:

    def __init__(self) -> None:
        self.financial_years = None
        self.auditors = None
        self.company_statuses = None
        self.categories = None
        self.letter_types = None
        self.company_types = None
        self.report_types = None
        self.url = 'https://search.codal.ir/api/search/v1/'

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

        try:
            CompanyStatuses.__table__.create(engine)
            CompanyTypes.__table__.create(engine)
            LetterTypes.__table__.create(engine)
            ReportTypes.__table__.create(engine)
            Auditors.__table__.create(engine)
            FinancialYears.__table__.create(engine)
        except Exception as e:
            print(e.__context__, end="\r", flush=True)

        fill_table_of_db_with_df(self.company_statuses, "company_statuses", "code")
        fill_table_of_db_with_df(self.report_types, "report_types", "code")
        fill_table_of_db_with_df(self.company_types, "company_types", "code")
        fill_table_of_db_with_df(self.letter_types, "letter_types", "code")
        fill_table_of_db_with_df(self.auditors, "auditors", "code")
        fill_table_of_db_with_df(self.financial_years, "financial_years", "date")


def fill_categories_table():
    cat = Categories()
    cat.fill_categories_table()


if __name__ == '__main__':
    pass
