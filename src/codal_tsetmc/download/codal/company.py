import pandas as pd

from codal_tsetmc import Companies
from codal_tsetmc.tools.api import get_dict_from_xml_api
from codal_tsetmc.tools.database import fill_table_of_db_with_df, create_table_if_not_exist


def get_companies():
    url = 'https://search.codal.ir/api/search/v1/companies'
    com = get_dict_from_xml_api(url)
    df = pd.DataFrame(com)
    df.columns = ["symbol", "name", "isic", "type_code", "status_code"]
    return df


def fill_companies_table():
    df = get_companies()
    create_table_if_not_exist(Companies)
    fill_table_of_db_with_df(df, "companies", "symbol")


if __name__ == '__main__':
    pass

