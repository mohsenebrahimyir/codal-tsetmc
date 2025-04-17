from codal_tsetmc.config.engine import (
    Column, Integer, String, Base
)
from sqlalchemy import BigInteger


class StockCapital(Base):
    __tablename__ = "stock_capital"

    id = Column(Integer, primary_key=True)
    code = Column(BigInteger)
    symbol = Column(String)
    date = Column(String)
    old = Column(BigInteger)
    new = Column(BigInteger)
    up_date = Column(BigInteger)

    def __repr__(self):
        return f"name: {self.symbol}"

