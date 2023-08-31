from codal_tsetmc.config.engine import engine
from codal_tsetmc.models.stocks import (
    Stocks,
    StockPrice,
    StockCapital,
    CommodityPrice
)
from codal_tsetmc.models.companies import (
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
        Model.__table__.create(engine)
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
