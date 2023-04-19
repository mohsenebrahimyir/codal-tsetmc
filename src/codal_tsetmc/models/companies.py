from codal_tsetmc.config import *
from sqlalchemy.orm import relationship


class CompanyTypes(Base):
    __tablename__ = "company_types"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)
    companies = relationship('Companies', backref='type')

    def __repr__(self):
        return f"({self.code}, {self.name})"

class CompanyStatuses(Base):
    __tablename__ = "company_statuses"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)
    companies = relationship('Companies', backref='status')

    def __repr__(self):
        return f"({self.code}, {self.name})"

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
        return f"({self.symbol}, {self.name}, {self.type.name}, {self.status.name})"


class ReportTypes(Base):
    __tablename__ = "report_types"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.name})"

class LetterTypes(Base):
    __tablename__ = "letter_types"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.name})"


class Auditors(Base):
    __tablename__ = "auditors"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.name})"
    

# class FinancialStatement(Base):
#     __tablename__ = "financial_statement"
    
#     id = Column(Integer, primary_key=True)
#     tracing_no = Column(Integer)
#     symbol = Column(String, ForeignKey("stocks.name"), index=True)
#     period = Column(Integer)
#     sent_date_time = Column(Integer)
#     publish_date_time = Column(Integer)
#     period_end_to_date = Column(Integer)
#     year_end_to_date = Column(Integer)
#     table_fa = Column(String)
#     table_en = Column(String)
#     alias_name = Column(String)
#     version_no = Column(Integer)
#     item_fa = Column(String)
#     item_en = Column(String)
#     value = Column(Integer)
#     is_audited = Column(Boolean)
#     is_consolidated = Column(Boolean)

#     def __repr__(self):
#         return f"(صورت مالی, {self.name})"
    
# class BalanceSheet(Base):
#     __tablename__ = "balance_sheet"
    
#     id = Column(Integer, primary_key=True)
#     tracing_no = Column(Integer)

#     def __repr__(self):
#         return f"(ترازنامه یا صورت وضعیت مالی, {self.name})"


