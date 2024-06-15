from codal_tsetmc.config.engine import Base
from sqlalchemy import Integer, Column, BigInteger, String


class FinancialYear(Base):
    __tablename__ = "financial_year"

    id = Column(Integer, primary_key=True)
    code = Column(BigInteger, unique=True)
    date = Column(String)

    def __repr__(self):
        return f"({self.date})"

