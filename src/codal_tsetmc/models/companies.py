from sqlalchemy.orm import relationship
import pandas as pd
import jalali_pandas

from codal_tsetmc.config.engine import (
    Column, Integer, String, Boolean, ForeignKey, Base
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


class FinancialStatementHeader(Base):
    __tablename__ = "financial_statement_header"

    id = Column(Integer, primary_key=True)
    tracing_no = Column(Integer, ForeignKey("letters.tracing_no"), index=True)
    name = Column(String)
    capital = Column(Integer)
    symbol = Column(String, ForeignKey("companies.symbol"), index=True)
    isic = Column(String)
    company_state = Column(String)
    title_fa = Column(String)
    title_en = Column(String)
    period_end_to_date = Column(Integer)
    year_end_to_date = Column(Integer)
    register_date_time = Column(Integer)
    sent_date_time = Column(Integer)
    publish_date_time = Column(Integer)
    period_extra_day = Column(Integer)
    is_consolidated = Column(Boolean)
    is_audited = Column(Boolean)
    audit_state = Column(Integer)
    state = Column(Integer)
    is_for_auditing = Column(Boolean)
    period = Column(Integer)

    def __repr__(self):
        return f"سربرگ صورت مالی"


class FinancialStatementTableWithSingleItem(Base):
    __tablename__ = "financial_statement_table_with_single_item"

    id = Column(Integer, primary_key=True)
    tracing_no = Column(Integer, ForeignKey("letters.tracing_no"), index=True)
    cell_id = Column(String, unique=True)
    sheet_title_fa = Column(String)
    sheet_title_en = Column(String)
    table_title_fa = Column(String)
    table_title_en = Column(String)
    alias_name = Column(String)
    period_end_to_date = Column(Integer)
    year_end_to_date = Column(Integer)
    description = Column(String)
    item = Column(String)
    value = Column(Integer)

    def __repr__(self):
        return f"جدول صورت مالی‌های با تک آیتم"
