import string
from codal_tsetmc.config import *
from sqlalchemy.orm import relationship
import pandas as pd
import jalali_pandas


class CompanyTypes(Base):
    __tablename__ = "company_types"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)
    companies = relationship('Companies', backref='type')
    
    def __repr__(self):
        return f'<Company Type: {self.name}>'

class CompanyStatuses(Base):
    __tablename__ = "company_statuses"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)
    companies = relationship('Companies', backref='status')
    
    def __repr__(self):
        return f'<Company Status: {self.name}>'

class Companies(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    name = Column(String)
    isic = Column(String, unique=True)
    type_code = Column(String, ForeignKey("company_types.code"), index=True)
    status_code = Column(String, ForeignKey("company_statuses.code"), index=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ReportTypes(Base):
    __tablename__ = "report_types"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)

class LetterTypes(Base):
    __tablename__ = "letter_types"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)


class Auditors(Base):
    __tablename__ = "auditors"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)