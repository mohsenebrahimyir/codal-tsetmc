import codal_tsetmc.config as db
from .stocks import (
    Stocks,
    StockPrice,
    StockCapital,
    CommodityPrice
)
from .companies import (
    Companies,
    CompanyTypes,
    CompanyStatuses,
    ReportTypes,
    LetterTypes,
    Auditors,
    Letters,
    FinancialStatementHeader,
    FinancialStatementTableWithSingleItem
)

def create_table(Model):
    try:
        Model.__table__.create(db.engine)
    except:
        pass

def create():
    models = [
        Stocks,
        StockPrice,
        StockCapital,
        Companies,
        CompanyTypes,
        CompanyStatuses,
        ReportTypes,
        LetterTypes,
        Auditors, 
        Letters,
        FinancialStatementHeader, 
        FinancialStatementTableWithSingleItem,
        CommodityPrice
    ]
    for model in models:
        create_table(model)
