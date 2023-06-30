from codal_tsetmc.config import *
from sqlalchemy.orm import relationship


class Companies(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, ForeignKey("stocks.name"), index=True)
    name = Column(String)
    isic = Column(String)
    type_code = Column(String, ForeignKey("company_types.code"), index=True)
    status_code = Column(String, ForeignKey("company_statuses.code"), index=True)

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
    company_symbol = Column(String, ForeignKey("companies.symbol"), index=True)
    company_name = Column(String)

    def __repr__(self):
        return f"(گزارشات کدال)"


class FinancialStatement(Base):
    __tablename__ = "financial_statement"
    
    id = Column(Integer, primary_key=True)
    head_company_name = Column(String)
    head_listed_capital = Column(Integer)
    head_symbol = Column(String)
    head_isic = Column(String)
    head_company_state = Column(String)
    datasource_tracing_no = Column(Integer, ForeignKey("letters.tracing_no"), index=True)
    datasource_title_fa = Column(String)
    datasource_title_en = Column(String)
    datasource_period_end_to_date = Column(Integer)
    datasource_year_end_to_date = Column(Integer)
    datasource_register_date_time = Column(Integer)
    datasource_sent_date_time = Column(Integer)
    datasource_publish_date_time = Column(Integer)
    datasource_period_extra_day = Column(Integer)
    datasource_is_consolidated = Column(Boolean)
    datasource_tracing_no = Column(Integer)
    datasource_is_audited = Column(Boolean)
    datasource_audit_state = Column(Integer)
    datasource_state = Column(Integer)
    datasource_is_for_auditing = Column(Boolean)
    datasource_type = Column(Integer)
    datasource_subject = Column(Integer)
    datasource_dsc = Column(Integer)
    datasource_period = Column(Integer)

    def __repr__(self):
        return f"(گزارشات صورت مالی)"
