import pandas as pd
import urllib
import json
from urllib.request import urlopen

import codal_tsetmc.config as db

from .string_edit import *


def get_dict_from_xml_api(url: str) -> dict:
    print(f"Get data from {url}")
    try:
        with urlopen(url) as file:
            string_json = file.read().decode('utf-8')
    except ConnectionError:
        print("fall back to manual mode")
        pass
    except Exception as e:
        print(e)
        pass
    return json.loads(string_json)


def fill_table_of_db_with_df(
    data: pd.DataFrame,
    table: str,
    columns: str,
    conditions: str = ""
):
    try:
        q = f"select {columns} from {table} {conditions}"
        temp = pd.read_sql(q, db.engine)
        data = data[~data[columns].isin(temp[columns])]
    except:
        pass

    data.to_sql(
        table, db.engine,
        if_exists="append",
        index=False
    )
    print(f"{table} update.")


def get_companies():
    #TODO: ...
    """_summary_

    Returns:
        _type_: _description_
    """
    url = 'https://search.codal.ir/api/search/v1/companies'
    com = get_dict_from_xml_api(url)
    df = pd.DataFrame(com)
    df.columns = ["symbol", "name", "isic", "type_code", "status_code"]
    return df


def fill_companies_table():
    #TODO
    """_summary_

    Returns:
        _type_: _description_
    """
    df = get_companies()
    fill_table_of_db_with_df(df, "companies", "symbol")
