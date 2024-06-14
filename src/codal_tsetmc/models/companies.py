from codal_tsetmc.config.engine import (
    Column, Integer, String, Base
)
from sqlalchemy import BigInteger


class Companies(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    name = Column(String)
    isic = Column(String)
    type_code = Column(String)
    status_code = Column(String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"({self.symbol}, "\
               f"{self.name}, "


class CompanyTypes(Base):
    __tablename__ = "company_types"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.title})"


class CompanyStatuses(Base):
    __tablename__ = "company_statuses"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.title})"


class ReportTypes(Base):
    __tablename__ = "report_types"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.title})"


class LetterTypes(Base):
    __tablename__ = "letter_types"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String, unique=True)

    def __repr__(self):
        return f"({self.code}, {self.title})"


class Auditors(Base):
    __tablename__ = "auditors"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    name = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.name})"


class FinancialYears(Base):
    __tablename__ = "financial_years"

    id = Column(Integer, primary_key=True)
    code = Column(BigInteger, unique=True)
    date = Column(String)

    def __repr__(self):
        return f"({self.date})"


class Letters(Base):
    __tablename__ = "letters"

    id = Column(Integer, primary_key=True)
    publish_date_time = Column(BigInteger)
    sent_date_time = Column(BigInteger)
    tracing_no = Column(BigInteger, unique=True)
    letter_serial = Column(String, unique=True)
    letter_title = Column(String)
    letter_code = Column(String)
    letter_types = Column(String)
    symbol = Column(String)
    name = Column(String)

    def __repr__(self):
        return f"tracing_no: {self.tracing_no}, "\
               f"serial: {self.letter_serial}"
