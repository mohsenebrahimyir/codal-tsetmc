import pandas as pd
import urllib
import json
from urllib.request import urlopen

import codal_tsetmc.config as db
from codal_tsetmc.models import Companies

from .string_edit import *


def get_dict_from_xml_api(url: str) -> dict:
    with urlopen(url) as file:
        string_json = file.read().decode('utf-8')
    return json.loads(string_json)


def get_companies():
    #TODO: ...
    """_summary_

    Returns:
        _type_: _description_
    """
    url = 'https://search.codal.ir/api/search/v1/companies'

    return get_dict_from_xml_api(url)

def fill_companies_table():
    pass


class Categories:
    #TODO: ...
    """_summary_
    """

    def __init__(self) -> None:
        self.url = 'https://search.codal.ir/api/search/v1/categories'

    def get_data(self):
        #TODO: ...
        """_summary_
        Returns:
            _type_: _description_
        """

        self.data = get_dict_from_xml_api(self.url)
        report_types = []
        company_types = []
        letter_types = []
        categories = []

        for item in self.data:
            publisher_types_items = item.pop("PublisherTypes")
            if item["Code"] != -1:
                for publisher_type in publisher_types_items:
                    letter_types_items = publisher_type.pop("LetterTypes")
                    for letter_type in letter_types_items:
                        if letter_type not in letter_types:
                            letter_types += [{
                                "code": letter_type["Id"],
                                "name": letter_type["Name"]
                            }]
                        categories += [{
                            "report_types_code": item["Code"],
                            "company_types_code": publisher_type["Code"],
                            "letter_type_code": letter_type["Id"],
                        }]
            else:
                for publisher_type in publisher_types_items:
                    company_types += [{
                        "code": publisher_type["Code"],
                        "name": publisher_type["Name"]
                    }]

            report_types += [{"code": item["Code"], "name": item["Name"]}]

        self.report_types = pd.DataFrame(report_types) \
            .sort_values("code").reset_index(drop=True)
        self.company_types = pd.DataFrame(company_types) \
            .sort_values("code").reset_index(drop=True)
        self.letter_types = pd.DataFrame(letter_types) \
            .drop_duplicates().sort_values("code").reset_index(drop=True)
        self.categories = pd.DataFrame(categories) \
            .drop_duplicates().reset_index(drop=True)
        self.company_status = pd.DataFrame({
            {"code": -1, "name": 'همه موارد'},
            {"code": 0, "name": 'پذیرفته شده در بورس تهران'},
            {"code": 1, "name": 'پذیرفته شده در فرابورس ایران'},
            {"code": 2, "name": 'ثبت شده پذیرفته نشده'},
            {"code": 3, "name": 'ثبت نشده نزد سازمان'},
            {"code": 4, "name": 'پذیرفته شده در بورس کالای ایران'},
            {"code": 5, "name": 'پذیرفته شده دربورس انرژی ایران'},
        }).sort_values("code").reset_index(drop=True)


def fill_company_status():
    pass


def fill_report_types():
    pass


def fill_company_types():
    pass


def fill_letter_types():
    pass


def get_financial_years():
    #TODO: ...
    """_summary_

    Returns:
        _type_: _description_
    """
    url = 'https://search.codal.ir/api/search/v1/financialYears'
    com = get_dict_from_xml_api(url)
    df = pd.DataFrame(com)
    df.columns = ["date"]

    return df


def fill_financial_years():
    pass


def get_auditors():
    #TODO: ...
    """_summary_

    Returns:
        _type_: _description_
    """
    url = 'https://search.codal.ir/api/search/v1/auditors'
    com = get_dict_from_xml_api(url)
    df = pd.DataFrame(com)
    df.columns = ["name", "code"]

    return df.sort_values("code").reset_index(drop=True)


def fill_auditors_table():
    pass
