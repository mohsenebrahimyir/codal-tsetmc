import pandas as pd

import codal_tsetmc.config as db
from codal_tsetmc.tools import get_dict_from_xml_api, fill_table_of_db_with_df
from ..tools.string_edit import *


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
