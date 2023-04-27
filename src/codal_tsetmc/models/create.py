import codal_tsetmc.config as db
from .stocks import (
    Stocks,
    StockPrice,
    StockClient,
    StockCapital,
    StockDividend,
    StockAdjusted,
)
from .companies import (
    Companies,
    CompanyTypes,
    CompanyStatuses,
    ReportTypes,
    LetterTypes,
    Auditors,
    Letters
)

def create_table(Model):
    try:
        Model.__table__.create(db.engine)
    except:
        pass

def create():
    models = [
        Stocks, StockPrice, StockClient, StockCapital,
        StockDividend, StockAdjusted, Companies, CompanyTypes,
        CompanyStatuses, ReportTypes, LetterTypes, Auditors,
        Letters
    ]
    for model in models:
        create_table(model)
