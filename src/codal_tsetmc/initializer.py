import os

from codal_tsetmc.models import (
    Stock,
    StockGroup,
    StockCapital,
    StockPrice,
    CompanyState,
    Company,
    LetterType,
    LetterGroup,
    ReportingType,
    Auditor,
    FinancialYear,
    CompanyType,
    IndustryGroup,
)

from codal_tsetmc.tools.database import (
    read_table_by_sql_query, create_table_if_not_exist
)
from codal_tsetmc.config.engine import CDL_TSE_FOLDER, HOME_PATH
from codal_tsetmc.models.create import create
from codal_tsetmc.download.codal.company import fill_companies_table
from codal_tsetmc.download.codal.category import fill_categories_table
from codal_tsetmc.download.tsetmc.stock import (
    fill_stocks_table, fill_stocks_groups_table
)
from codal_tsetmc.download.tsetmc.price import fill_stocks_prices_table
from codal_tsetmc.download.tsetmc.capital import fill_stocks_capitals_table


def create_db():
    print("creating database")
    path = os.path.join(HOME_PATH, CDL_TSE_FOLDER)
    try:
        os.mkdir(path)
        print("making package folder...")
        print(
            """
            Includes: config.yml and companies-stocks.db
            if you are using sqlite.
            """
        )
        print("you can change config.yml to your needs.")
    except FileExistsError:
        print("folder already exists")
    create()
    print(f"Database created in: {path}")


def init_db():
    print("downloading company and stock info from CODAL and TSETMC")
    models = [
        FinancialYear, Auditor,
        LetterType, LetterGroup,
        ReportingType, CompanyState,
        CompanyType, IndustryGroup
    ]
    for model in models:
        create_table_if_not_exist(model)

    for model in models:
        df = read_table_by_sql_query(
            f"SELECT * FROM {model.__tablename__} LIMIT 1;"
        )
        if df.empty:
            fill_categories_table()

    create_table_if_not_exist(Company)
    df = read_table_by_sql_query(
        f"SELECT * FROM {Company.__tablename__} LIMIT 1;"
    )
    if df.empty:
        fill_companies_table()


def fill_db():
    print("downloading company and stock details from CODAL and TSETMC")
    print("may take few minutes")
    fill_stocks_table()
    fill_stocks_prices_table()
    fill_stocks_capitals_table()
    print("For more info go to:")
    print("https://github.com/mohsenebrahimyir/codal-tsetmc")


if __name__ == '__main__':
    pass
