import os

from codal_tsetmc import db, models
from codal_tsetmc.download import (
    Categories,
    fill_stock_table,
    fill_companies_table
)


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


def fill_db():
    print("downloading company and stock details from CODAL and TSETMC")
    print("may take few minutes")
    fill_stock_table()
    fill_companies_table()
    cat = Categories()
    cat.fill_categories_table()
    print("For more info go to:")
    print("https://github.com/mohsenebrahimyir/codal-tsetmc")
