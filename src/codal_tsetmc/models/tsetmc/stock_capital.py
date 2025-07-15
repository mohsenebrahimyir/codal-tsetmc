from sqlalchemy import Column, BigInteger, Integer, String
from ...config.engine import Base


class StockCapital(Base):
    __tablename__ = "stock_capital"

    id = Column(Integer, primary_key=True)
    code = Column(BigInteger)
    symbol = Column(String)
    date = Column(Integer)
    old = Column(BigInteger)
    new = Column(BigInteger)
    up_date = Column(Integer)

    def __repr__(self):
        return f"name: {self.symbol}"

