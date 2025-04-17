from codal_tsetmc.config.engine import (
    Column, Integer, String, Base
)
from sqlalchemy import BigInteger, Float


class StockPrice(Base):
    __tablename__ = "stock_price"

    id = Column(Integer, primary_key=True)
    code = Column(BigInteger)
    symbol = Column(String)
    date = Column(String)
    volume = Column(BigInteger)
    value = Column(BigInteger)
    price = Column(Float)
    up_date = Column(BigInteger)

    def __repr__(self):
        return f"(symbol: {self.symbol}, code: {self.code})"

