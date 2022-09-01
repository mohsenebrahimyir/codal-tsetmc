import pandas as pd
import urllib
import json
import codal_tsetmc.config as db
from codal_tsetmc.models import Companies

from string_edit import *


def get_companies():
    """
    Download companies detail and save them to the database.
    better not use it alone.
    Its not useful after first setup. ;)
    
    params
    TODO: fill parameter of functions
    ----------------
    symbol:
    name:
    isic:
    type:
    status:
    """
    url = 'https://search.codal.ir/api/search/v1/companies'
    with urllib.request.urlopen(url) as file:
        r = file.read().decode('utf-8')

    return json.loads(r)


def create_or_update_stock_from_dict(company_id, stock):
    if exist := Companies.query.filter_by(isic=company_id).first():
        print(f"stock with isic {company_id} exist")
        exist.symbol = stock["sy"]
        exist.name = stock["n"]
        exist.type = stock["t"]
        exist.status = stock["st"]
    else:
        print(f"creating stock with code {company_id}")
        db.session.add(Companies(**stock))


def fill_company_table():
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
        with urllib.request.urlopen(self.url) as file:
            data = file.read().decode('utf-8')

        self.data = json.loads(data)
        report_types = []
        company_types = []
        letter_types = []
        categories = []

        for item in json.loads(data):
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


def get_financial_years():
    #TODO: ...
    """_summary_

    Returns:
        _type_: _description_
    """
    url = 'https://search.codal.ir/api/search/v1/financialYears'
    with urllib.request.urlopen(url) as file:
        com = file.read().decode('utf-8')

    df = pd.read_json(com)
    df.columns = ["date"]

    return df


def get_auditors():
    #TODO: ...
    """_summary_

    Returns:
        _type_: _description_
    """
    url = 'https://search.codal.ir/api/search/v1/auditors'
    with urllib.request.urlopen(url) as file:
        com = file.read().decode('utf-8')

    df = pd.read_json(com)
    df.columns = ["name", "code"]

    return df.sort_values("code").reset_index(drop=True)
