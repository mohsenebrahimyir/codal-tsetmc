import os

import codal_tsetmc.config as db
from .download import (
    Categories,
    CodalQuery,
    get_all_price,
    get_stock_detail,
    get_stock_groups,
    get_stock_ids,
    update_group_price,
    update_stock_price,
    get_companies,
    fill_companies_table,
    fill_categories_table,
    get_commodity_price_history,
    fill_commodity_price_table
)
from codal_tsetmc.models import (
    Stocks,
    StockPrice,
    StockCapital,
    get_asset,
    Companies,
    CompanyTypes,
    CompanyStatuses,
    ReportTypes,
    LetterTypes,
    Auditors,
    Letters
)

from codal_tsetmc.tools import (
    plot_olhcv
)

from .initializer import init_db, fill_db


def db_is_empty():
    try:
        db.session.execute("select * from stocks limit 1;")
        return False
    except:
        return True


if db_is_empty():
    print("No database founded.")
    init_db()
    fill_db()
