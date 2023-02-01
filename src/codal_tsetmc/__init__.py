import os

import codal_tsetmc.config as db
from .download import (
    Categories,
    CodalQuery,
    get_all_price,
    get_all_client,
    get_stock_detail,
    get_stock_groups,
    get_stock_ids,
    update_group_price,
    update_group_client,
    update_group_dividend,
    update_group_capital,
    update_group_adjusted,
    update_stock_price,
    update_stock_client,
    update_stock_dividend,
    update_stock_capital,
    update_stock_adjusted,
    get_companies,
    fill_companies_table,
    get_commodity_price_history,
    fill_commodity_price_table
)
from codal_tsetmc.models import (
    Stocks,
    StockPrice,
    StockClient,
    StockDividend,
    StockCapital,
    StockAdjusted,
    get_asset,
    Companies,
    CompanyTypes,
    CompanyStatuses,
    ReportTypes,
    LetterTypes,
    Auditors,
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
