from sqlalchemy.sql import text

from codal_tsetmc.config import engine as db
from codal_tsetmc.config.engine import (
    HOME_PATH,
    CDL_TSE_FOLDER,
    default_db_path,
    CONFIG_PATH
)

from codal_tsetmc.tools.database import (
    read_table_by_conditions,
    read_table_by_sql_query,
    fill_table_of_db_with_df
)

from codal_tsetmc.models.stocks import (
    Stocks,
    StocksPrices,
    StocksCapitals,
    StocksGroups,
    CommoditiesPrices
)

from codal_tsetmc.models.companies import (
    Companies,
    CompanyTypes,
    CompanyStatuses,
    LetterTypes,
    Letters,
    FinancialYears
)

from codal_tsetmc.download.codal.query import CodalQuery

from codal_tsetmc.download.tsetmc.stock import (
    get_stock_detail,
    get_stock_ids,
    get_stocks_groups,
    update_stock_table,
    update_stocks_table,
    fill_stocks_groups_table,
    fill_stocks_table
)

from codal_tsetmc.download.tsetmc.price import (
    get_stock_price_daily,
    get_stock_prices_history,
    get_index_prices_history,
    update_stock_prices,
    update_index_prices,
    update_stocks_prices,
    update_stocks_group_prices,
    fill_stocks_prices_table
)

from codal_tsetmc.download.tsetmc.capital import (
    get_stock_capital_daily,
    get_stock_capitals_history,
    update_stock_capitals,
    update_stocks_capitals,
    update_stocks_group_capitals,
    fill_stocks_capitals_table
)

from codal_tsetmc.initializer import (
    create_db,
    init_db,
    fill_db,
    fill_companies_table,
    fill_categories_table,
    fill_commodities_prices_table
)


def db_is_empty():
    try:
        for table in [
            "companies", "company_types", "company_statuses",
            "report_types", "letter_types", "auditors",
            "financial_years", "stocks_groups", "stocks"
        ]:
            db.session.execute(text(f"select * from {table} limit 1;"))

        return False
    except Exception as e:
        print("db_is_empty: ", e.__context__, end="\r", flush=True)
        return True


if db_is_empty():
    create_db()
    init_db()
