from sqlalchemy import Column, BigInteger, Integer, String, BigInteger, Float
from ...config.engine import Base


class StockPrice(Base):
    __tablename__ = "stock_price"

    id = Column(Integer, primary_key=True)
    code = Column(BigInteger)
    symbol = Column(String)
    date = Column(String)
    volume = Column(BigInteger)
    value = Column(BigInteger)
    price = Column(Float)
    up_date = Column(Integer)

    def __repr__(self):
        return f"(symbol: {self.symbol}, code: {self.code})"
