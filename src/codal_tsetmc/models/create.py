from codal_tsetmc.config.engine import engine
from . import (
    Stock,
    StockPrice,
    StockCapital,
    StockGroup,
    Company,
    CompanyType,
    CompanyState,
    FinancialYear,
    ReportType,
    LetterType,
    Auditor,
    Letter
)

models = [
    Auditor,
    FinancialYear,
    ReportType,
    LetterType,
    CompanyType,
    CompanyState,
    Company,
    Letter,
    StockGroup,
    Stock,
    StockPrice,
    StockCapital,
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
