import os

from codal_tsetmc import db, models
from codal_tsetmc.download import *


def init_db():
    print("creating database")
    path = os.path.join(db.HOME_PATH, db.CDL_TSE_FOLDER)
    try:
        os.mkdir(path)
        print("making package folder...")
        print("Includes: config.yml and companies-stocks.db  if you are using sqlite.")
        print("you can change config.yml to your needs.")
    except FileExistsError:
        print("folder already exists")
    models.create()
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
    print("For more info go to:")
    print("https://github.com/mohsenebrahimyir/codal-tsetmc")


if __name__ == '__main__':
    pass
