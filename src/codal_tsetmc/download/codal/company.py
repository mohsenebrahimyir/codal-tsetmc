import pandas as pd

from codal_tsetmc import Companies
from codal_tsetmc.config.engine import engine
from codal_tsetmc.tools.api import get_dict_from_xml_api
from codal_tsetmc.tools.database import fill_table_of_db_with_df


def get_companies():
    url = 'https://search.codal.ir/api/search/v1/companies'
    com = get_dict_from_xml_api(url)
    df = pd.DataFrame(com)
    df.columns = ["symbol", "name", "isic", "type_code", "status_code"]
    return df


def fill_companies_table():
    df = get_companies()

    try:
        Companies.__table__.create(engine)
    except Exception as e:
        print(e.__context__, end="\r", flush=True)

    fill_table_of_db_with_df(df, "companies", "symbol")


if __name__ == '__main__':
    pass

