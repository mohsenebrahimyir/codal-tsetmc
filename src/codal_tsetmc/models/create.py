from codal_tsetmc.config.engine import engine
from codal_tsetmc.models.stocks import (
    Stocks,
    StocksPrices,
    StocksCapitals,
    StocksGroups
)
from codal_tsetmc.models.companies import (
    Companies,
    CompanyTypes,
    CompanyStatuses,
    FinancialYears,
    ReportTypes,
    LetterTypes,
    Auditors,
    Letters
)

models = [
    Stocks,
    StocksPrices,
    StocksCapitals,
    StocksGroups,
    Companies,
    CompanyTypes,
    CompanyStatuses,
    FinancialYears,
    ReportTypes,
    LetterTypes,
    Auditors,
    Letters
]


def create_table(model):
    try:
        model.__table__.create(engine)
        return True

    except Exception as e:
        print(e.__context__)
        return False


def create():
    for model in models:
        create_table(model)
