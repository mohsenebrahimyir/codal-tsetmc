import os

from codal_tsetmc import db, models, get_all_price
from codal_tsetmc.download import fill_stock_table


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
    print("downloading company and stock details from COSAL and TSETMC")
    print("may take few minutes")

    fill_stock_table()
    print("Stock table is available now, example:")
    print("from codal_tsetmc import Stocks")
    print('stock = Stocks.query.filter_by(symbol="کگل").first()')


    a = input("Do you want to download all price? [y,(n)]")
    if a == "y":
        print("Downloading price:")
        get_all_price()
    else:
        print("if you want download all prices use codal_tsetmc.get_all_price() ")
        print("if you want download price history of a specfic stock use: ")
        print("stock.update_price()")
        print("or use codal_tsetmc.update_group_price(id) ")
        print("For more info go to:")
        print("https://github.com/mohsenebrahimyir/codal-tsetmc")
