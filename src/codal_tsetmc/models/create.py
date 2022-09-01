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
)


def create():
    Stocks.__table__.create(db.engine)
    StockPrice.__table__.create(db.engine)
    StockClient.__table__.create(db.engine)
    StockCapital.__table__.create(db.engine)
    StockDividend.__table__.create(db.engine)
    StockAdjusted.__table__.create(db.engine)
    Companies.__table__.create(db.engine)
    CompanyTypes.__table__.create(db.engine)
    CompanyStatuses.__table__.create(db.engine)
    ReportTypes.__table__.create(db.engine)
    LetterTypes.__table__.create(db.engine)
    Auditors.__table__.create(db.engine)
