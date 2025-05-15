from codal_tsetmc.config.engine import (
    HOME_PATH,
    CDL_TSE_FOLDER,
    default_db_path,
    CONFIG_PATH,
)
from codal_tsetmc.tools.database import (
    read_table_by_conditions,
    read_table_by_sql_query,
    fill_table_of_db_with_df,
    is_table_exist_in_db,
)
from codal_tsetmc.models import (
    Stock,
    StockPrice,
    StockCapital,
    StockGroup,
    Company,
    CompanyType,
    CompanyState,
    LetterType,
    LetterGroup,
    IndustryGroup,
    ReportingType,
    Letter,
    FinancialYear,
    Auditor,
)
from codal_tsetmc.download.codal.query import CodalQuery
from codal_tsetmc.download.tsetmc.stock import (
    get_stock_detail,
    get_stock_ids,
    get_stocks_groups,
    update_stock_table,
    update_stocks_table,
    fill_stocks_groups_table,
    fill_stocks_table,
)
from codal_tsetmc.download.tsetmc.price import (
    get_stock_price_daily,
    get_stock_prices_history,
    get_index_prices_history,
    update_stock_prices,
    update_index_prices,
    update_indexes_prices,
    update_stocks_prices,
    update_stocks_group_prices,
    fill_stocks_prices_table,
)
from codal_tsetmc.download.tsetmc.capital import (
    get_stock_capital_daily,
    get_stock_capitals_history,
    update_stock_capitals,
    update_stocks_capitals,
    update_stocks_group_capitals,
    fill_stocks_capitals_table,
)
from codal_tsetmc.initializer import (
    create_db,
    init_db,
    fill_db,
    fill_companies_table,
    fill_categories_table,
)


def db_is_empty():
    init_models = [
        Company, CompanyState, CompanyType, IndustryGroup,
        LetterType, LetterGroup, ReportingType, Auditor, FinancialYear
    ]

    try:
        for model in init_models:
            table = model.__tablename__
            df = read_table_by_sql_query(f"SELECT * FROM {table} LIMIT 1;")
            if df.empty:
                return True

        return False
    except Exception as e:
        print(e.__context__)
        return True


if db_is_empty():
    create_db()
    init_db()
