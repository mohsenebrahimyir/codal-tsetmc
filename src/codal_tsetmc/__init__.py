import os

from codal_tsetmc.tools.database import read_table_by_conditions
from codal_tsetmc.models.stocks import Stocks
from codal_tsetmc.models.companies import Companies
from codal_tsetmc.download.codal.query import CodalQuery

from .config import  engine as db
from .initializer import (
    init_db, 
    fill_db,
    fill_companies_table,
    fill_categories_table,
    fill_interim_financial_statements_letters,
    fill_stocks_table,
    fill_stocks_prices_table,
    fill_stocks_capitals_table,
    fill_commodities_prices_table,
)


def db_is_empty():
    try:
        db.session.execute("select * from stocks limit 1;")
        return False
    except:
        return True


if db_is_empty():
    print("No database founded.")
    init_db()
