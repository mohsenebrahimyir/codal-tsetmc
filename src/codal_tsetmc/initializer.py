import os

from codal_tsetmc.models.stocks import Stocks, StocksGroups

from codal_tsetmc.models.companies import (
    CompanyStatuses, Companies, LetterTypes, ReportTypes, Auditors, FinancialYears, CompanyTypes
)

from codal_tsetmc.tools.database import read_table_by_sql_query

from codal_tsetmc.config.engine import CDL_TSE_FOLDER, HOME_PATH
from codal_tsetmc.models.create import create
from codal_tsetmc.download.codal.company import fill_companies_table
from codal_tsetmc.download.codal.category import fill_categories_table
from codal_tsetmc.download.tsetmc.stock import fill_stocks_table, fill_stocks_groups_table
from codal_tsetmc.download.tsetmc.price import fill_stocks_prices_table
from codal_tsetmc.download.tsetmc.capital import fill_stocks_capitals_table
from codal_tsetmc.download.other.commodity import fill_commodities_prices_table


def create_db():
    print("creating database")
    path = os.path.join(HOME_PATH, CDL_TSE_FOLDER)
    try:
        os.mkdir(path)
        print("making package folder...")
        print("Includes: config.yml and companies-stocks.db  if you are using sqlite.")
        print("you can change config.yml to your needs.")
    except FileExistsError:
        print("folder already exists")
    create()
    print(f"Database created in: {path}")


def init_db():
    print("downloading company and stock info from CODAL and TSETMC")
    models = [
        CompanyStatuses, CompanyTypes,
        LetterTypes, ReportTypes,
        Auditors, FinancialYears
    ]

    for model in models:
        table = model.__tablename__
        df = read_table_by_sql_query(f"SELECT * FROM {table} LIMIT 1;")
        if df.empty:
            fill_categories_table()

    df = read_table_by_sql_query(f"SELECT * FROM {Companies.__tablename__} LIMIT 1;")
    if df.empty:
        fill_companies_table()

    df = read_table_by_sql_query(f"SELECT * FROM {StocksGroups.__tablename__} LIMIT 1;")
    if df.empty:
        fill_stocks_groups_table()

    df = read_table_by_sql_query(f"SELECT * FROM {Stocks.__tablename__} LIMIT 1;")
    if df.empty:
        fill_stocks_table()


def fill_db():
    print("downloading company and stock details from CODAL and TSETMC")
    print("may take few minutes")
    fill_stocks_prices_table()
    fill_stocks_capitals_table()
    fill_commodities_prices_table()
    print("For more info go to:")
    print("https://github.com/mohsenebrahimyir/codal-tsetmc")


if __name__ == '__main__':
    pass
