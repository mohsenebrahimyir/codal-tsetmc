import pandas as pd

from ...models import (
    CompanyState,
    CompanyType,
    CompanyNature,
    LetterType,
    LetterGroup,
    Auditor,
    FinancialYear,
    IndustryGroup,
)
from ...tools.api import get_dict_from_xml_api
from ...tools.database import fill_table_of_db_with_df, create_table_if_not_exist
from ...tools.string import date_to_digit, REPLACE_INCORRECT_CHARS


models = [
    CompanyState,
    CompanyType,
    LetterType,
    LetterGroup,
    Auditor,
    FinancialYear,
    CompanyNature,
    IndustryGroup,
]


class Categories:

    def __init__(self) -> None:
        self.url = "https://search.codal.ir/api/search/v1/"
        self.result = {}

    def get_data(self):
        api = get_dict_from_xml_api(self.url + "categories")
        company_types = []
        letter_types = []
        letter_groups = []
        categories = []

        if not api:
            raise Exception("Check Network connection")

        for item in api:
            publisher_types_items = item.pop("PublisherTypes")
            if item["Code"] != -1:
                for publisher_type in publisher_types_items:
                    letter_types_items = publisher_type.pop("LetterTypes")
                    for letter_type in letter_types_items:
                        if letter_type not in letter_types:
                            letter_types += [
                                {
                                    "code": letter_type["Id"],
                                    "title": letter_type["Name"],
                                }
                            ]
                        categories += [
                            {
                                "report_type_code": pd.to_numeric(item["Code"]),
                                "company_type_code": pd.to_numeric(
                                    publisher_type["Code"]
                                ),
                                "letter_type_code": pd.to_numeric(letter_type["Id"]),
                            }
                        ]
            else:
                for publisher_type in publisher_types_items:
                    company_types += [
                        {
                            "code": pd.to_numeric(publisher_type["Code"]),
                            "title": publisher_type["Name"],
                        }
                    ]

            letter_groups += [{"code": item["Code"], "title": item["Name"]}]

        self.result["letter_group"] = (
            pd.DataFrame(letter_groups).sort_values("code").reset_index(drop=True)
        )
        self.result["company_type"] = pd.DataFrame(company_types)
        self.result["company_type"].loc[-1] = [-1, "همه موارد"]
        self.result["company_type"] = (
            self.result["company_type"].sort_values("code").reset_index(drop=True)
        )

        self.result["letter_type"] = (
            pd.DataFrame(letter_types)
            .drop_duplicates()
            .sort_values("code")
            .reset_index(drop=True)
        )
        self.result["category"] = (
            pd.DataFrame(categories).drop_duplicates().reset_index(drop=True)
        )
        self.result["company_state"] = (
            pd.DataFrame(
                {
                    "code": [-1, 0, 1, 2, 3, 4, 5],
                    "title": [
                        "همه موارد",
                        "پذیرفته شده در بورس تهران",
                        "پذیرفته شده در فرابورس ایران",
                        "ثبت شده پذیرفته نشده",
                        "ثبت نشده نزد سازمان",
                        "پذیرفته شده در بورس کالای ایران",
                        "پذیرفته شده دربورس انرژی ایران",
                    ],
                }
            )
            .sort_values("code")
            .reset_index(drop=True)
        )

        self.result["company_nature"] = (
            pd.DataFrame(
                {
                    "code": [
                        -1,
                        1000000,
                        1000001,
                        1000002,
                        1000003,
                        1000004,
                        1000005,
                        1000006,
                        1000007,
                        1000008,
                        1000009,
                    ],
                    "title": [
                        "همه موارد",
                        "تولیدی",
                        "ساختمانی",
                        "سرمایه گذاری",
                        "بانک",
                        "لیزینگ",
                        "خدماتی",
                        "بیمه",
                        "حمل و نقل دریایی",
                        "کشاورزی",
                        "تامین سرمایه",
                    ],
                }
            )
            .sort_values("code")
            .reset_index(drop=True)
        )

        api = get_dict_from_xml_api(self.url + "auditors")
        self.result["auditor"] = pd.DataFrame(api)
        self.result["auditor"].columns = ["title", "code"]
        self.result["auditor"].sort_values("code").reset_index(drop=True, inplace=True)

        api = get_dict_from_xml_api(self.url + "financialYears")
        self.result["financial_year"] = pd.DataFrame(api)
        self.result["financial_year"].columns = ["title"]
        self.result["financial_year"]["code"] = self.result["financial_year"][
            "title"
        ].apply(date_to_digit)

        api = get_dict_from_xml_api(self.url + "IndustryGroup")
        self.result["industry_group"] = pd.DataFrame(api)
        self.result["industry_group"].columns = ["code", "title"]
        self.result["industry_group"].loc[-1] = [-1, "همه موارد"]
        self.result["industry_group"].sort_values("code").reset_index(
            drop=True, inplace=True
        )

    def fill_categories_table(self):
        self.get_data()
        for model in models:
            tablename = model.__tablename__
            create_table_if_not_exist(model)
            df = self.result[tablename].copy()
            for col in ["title"]:
                try:
                    if col in df.columns and df[col].notna().any():
                        df[col] = df[col].replace(regex=REPLACE_INCORRECT_CHARS)
                except Exception as e:
                    print(f"Data cleaning warning: {e}")
                    print(col)

            fill_table_of_db_with_df(df=df, table=tablename, unique="code")


def fill_categories_table():
    cat = Categories()
    cat.fill_categories_table()


if __name__ == "__main__":
    pass
