from sqlalchemy.orm import relationship

from codal_tsetmc.config.engine import (
    Column, Integer, String, ForeignKey, Base
)


class Companies(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, ForeignKey("stocks.name"), index=True)
    name = Column(String)
    isic = Column(String)
    type_code = Column(String, ForeignKey("company_types.code"), index=True)
    status_code = Column(String, 
                         ForeignKey("company_statuses.code"), index=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"({self.symbol}, {self.name}, {self.type.title}, {self.status.title})"


class CompanyTypes(Base):
    __tablename__ = "company_types"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)
    companies = relationship('Companies', backref='type')

    def __repr__(self):
        return f"({self.code}, {self.title})"


class CompanyStatuses(Base):
    __tablename__ = "company_statuses"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)
    companies = relationship('Companies', backref='status')

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
    title = Column(String)

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
    date = Column(Integer, unique=True)

    def __repr__(self):
        return f"({self.date})"


class Letters(Base):
    __tablename__ = "letters"

    id = Column(Integer, primary_key=True)
    publish_date_time = Column(Integer)
    sent_date_time = Column(Integer)
    tracing_no = Column(Integer, unique=True)
    letter_serial = Column(String, unique=True)
    letter_title = Column(String)
    letter_code = Column(String)
    letter_types = Column(String, ForeignKey("letter_types.title"), index=True)
    symbol = Column(String, ForeignKey("companies.symbol"), index=True)
    name = Column(String)

    def __repr__(self):
        return f"(گزارشات کدال)"

