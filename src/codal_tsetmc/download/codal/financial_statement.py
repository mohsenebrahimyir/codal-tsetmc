from mailbox import NotEmptyError
import os
import re
from symtable import Symbol
import sys
import time
import xmltodict
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from codal_tsetmc.models import Companies
from .query import CodalQuery
from .string_edit import *


def get_company_finantial_statement_list(
    symbol: str = None,
    name: str = None,
    isic: int = None
) -> pd.DataFrame:
    """_summary_ 
    TODO: fill description

    Returns:
        _type_: _description_
    """
    q = CodalQuery()
    if isic != None:
        q.set_isic(isic)
        company = Companies.query.filter_by(isic=isic).first()
        q.set_symbol(company.symbol)
    elif symbol != None:
        q.set_symbol(symbol)
        company = Companies.query.filter_by(symbol=symbol).first()
        q.set_isic(company.isic)
    elif name != None:
        company = Companies.query.filter_by(name=name).first()
        q.set_symbol(company.symbol)
        q.set_isic(company.isic)
    else:
        raise NotEmptyError(
            "please put the one of symbol, name or isic for company")

    q.set_from_date("1398/01/01")
    q.set_category('اطلاعات و صورت مالی سالانه')
    q.set_letter_type('اطلاعات و صورتهای مالی میاندوره ای')
    q.set_childs(False)

    return q.get_letters()


def get_companies_finantial_statement_list():
    """_summary_ 
    TODO: fill description

    Returns:
        _type_: _description_
    """
    q = CodalQuery()
    q.set_from_date("1398/01/01")
    q.set_category('اطلاعات و صورت مالی سالانه')
    q.set_letter_type('اطلاعات و صورتهای مالی میاندوره ای')
    q.set_childs(False)
    return q.get_letters()


class OpenCodalWithBrowser:

    def __init__(self):
        self.browser_status = False

    def open_browser(self):
        os.path.dirname(sys.executable)
        self.service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        time.sleep(1)
        print("=" * 50)
        print(f"Open chrome")
        self.browser_status = True

    def get_page_with_url(self):
        if not self.browser_status:
            self.open_browser()
        self.driver.get(self.url)


class SymbolFinancialStatementsForYear(OpenCodalWithBrowser):

    def __init__(self):
        super().__init__()

    def set_letter_info(self, symbol, url, fiscal_year, publish_datetime):
        self.url = url
        self.symbol = symbol
        self.fiscal_year = fiscal_year
        self.publish_datetime = publish_datetime
        self.options_value_and_text()

    def options_value_and_text(self):
        self.get_page_with_url()
        elems = self.driver.find_elements(
            By.XPATH, '//select[@id="ddlTable"]//option'
        )
        self.options = {
            elem.text: elem.get_attribute("value") for elem in elems
        }

    def open_option(self, option):
        value = self.options[option]
        url = f"{self.url}&sheetId={value}"
        self.driver.get(url)

    def add_description(self, df):
        count_null = df.isnull().sum(axis=1)
        null_index = df[count_null == max(count_null)].index
        desc = []
        for i in df.index:
            if i in null_index:
                desc_val = df[["variable"]].iloc[i]

            desc.append(desc_val)
        df["description"] = np.array(desc)

        return df

    def get_df_with_one_column(self, table=0):
        df = pd.read_html(self.driver.page_source)[table]
        df.columns = ["variable", "value"] + [""] * (len(df.columns)-2)
        df = self.add_description(df)
        df = df[["description", "variable", "value"]].dropna()
        df["fiscal_year"] = self.fiscal_year
        df["symbol"] = self.symbol
        df["publish_datetime"] = self.publish_datetime
        df["value"] = df.value.apply(pd.to_numeric)
        return df.replace(regex={"value": FIX_DIGITS})

    def get_statement_one_column(self, option):
        self.open_option(option)
        df = self.get_df_with_one_column()
        df["statement"] = option
        return df

    def get_consolidated_income_statement(self):
        option = "صورت سود و زیان تلفیقی"
        if option not in self.options.keys():
            return pd.DataFrame(columns=[
                "description", "variable",
                "value", "fiscal_year",
                "symbol", "statement",
                "publish_datetime"
            ])

        return self.get_statement_one_column(option)
