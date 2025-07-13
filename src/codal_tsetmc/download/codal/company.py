import pandas as pd

from ...models.codal.company import Company
from ...tools.api import get_dict_from_xml_api
from ...tools.database import (
    fill_table_of_db_with_df,
    create_table_if_not_exist
)
from ...tools.string import REPLACE_INCORRECT_CHARS


def get_companies():
    url = 'https://search.codal.ir/api/search/v1/companies'
    com = get_dict_from_xml_api(url)
    df = pd.DataFrame(com)
    df.columns = df.columns.str.lower()
    df.columns = [
        "symbol",
        "name",
        "isic",
        "type",
        "status",
        "industry",
        "nature",
    ]

    for col in [
        "type",
        "status",
        "industry",
        "nature",
    ]:
        df[col] = pd.to_numeric(df[col])

    return df.drop_duplicates(subset="symbol").reset_index(drop=True).copy()


def fill_companies_table():
    df = get_companies()
    create_table_if_not_exist(Company)
    for col in ["symbol", "name"]:
        try:
            if col in df.columns and df[col].notna().any():
                df[col] = df[col].replace(regex=REPLACE_INCORRECT_CHARS)
        except Exception as e:
            print(f"Data cleaning warning: {e}")
            print(col)
    
    fill_table_of_db_with_df(
        df=df,
        table=Company.__tablename__, 
        unique="symbol"
    )


if __name__ == '__main__':
    pass
