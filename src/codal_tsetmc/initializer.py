import os

from codal_tsetmc.config.engine import CDL_TSE_FOLDER, HOME_PATH
from codal_tsetmc.models.create import create
from codal_tsetmc.download.codal.company   import fill_companies_table
from codal_tsetmc.download.codal.category  import fill_categories_table
from codal_tsetmc.download.tsetmc.stock    import fill_stocks_table
from codal_tsetmc.download.tsetmc.price    import fill_stocks_prices_table
from codal_tsetmc.download.tsetmc.capital  import fill_stocks_capitals_table
from codal_tsetmc.download.other.commodity import fill_commodities_prices_table
from codal_tsetmc.download.codal.letters   import fill_interim_financial_statements_letters




def init_db():
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
    print(f"DataBase created in: {path}")
    fill_companies_table()
    fill_categories_table()


def fill_db():
    print("downloading company and stock details from CODAL and TSETMC")
    print("may take few minutes")
    fill_stocks_table()
    fill_stocks_prices_table()
    fill_stocks_capitals_table()
    fill_commodities_prices_table()
    fill_interim_financial_statements_letters()
    print("For more info go to:")
    print("https://github.com/mohsenebrahimyir/codal-tsetmc")


if __name__ == '__main__':
    pass
