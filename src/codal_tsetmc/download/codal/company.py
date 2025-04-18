import pandas as pd

from codal_tsetmc import Company
from codal_tsetmc.tools.api import get_dict_from_xml_api
from codal_tsetmc.tools.database import (
    fill_table_of_db_with_df,
    create_table_if_not_exist
)


def get_companies():
    url = 'https://search.codal.ir/api/search/v1/companies'
    com = get_dict_from_xml_api(url)
    df = pd.DataFrame(com)
    df.columns = df.columns.str.lower()
    df.columns = [
        "symbol",
        "name",
        "isic",
        "type_code",
        "status_code",
        "industry_group_code",
        "reporting_type",
    ]

    for col in [
        "isic",
        "type_code",
        "status_code",
        "industry_group_code",
        "reporting_type",
    ]:
        df[col] = pd.to_numeric(df[col])

    df = df.drop_duplicates("symbol")
    return df


def fill_companies_table():
    df = get_companies()
    create_table_if_not_exist(Company)
    fill_table_of_db_with_df(df, Company.__tablename__, "symbol")


if __name__ == '__main__':
    pass
