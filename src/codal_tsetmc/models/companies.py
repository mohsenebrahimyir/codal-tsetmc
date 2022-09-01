import string
from codal_tsetmc.config import *
from sqlalchemy.orm import relationship
import pandas as pd
import jalali_pandas


class CompanyTypes(Base):
    __tablename__ = "company_types"
    
    id = Column(Integer, primary_key=True)
    code = column(String, unique=True)
    name = Column(String, unique=True)
    companies = relationship("Companies", backref="type")


class CompanyStatus(Base):
    __tablename__ = "company_status"
    
    id = Column(Integer, primary_key=True)
    code = column(String, unique=True)
    name = Column(String, unique=True)
    companies = relationship("Companies", backref="status")

class Companies(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True)
    name = Column(String, unique=True)
    isic = Column(String, unique=True)
    type = Column(String, ForeignKey("company_types.code"), index=True)
    status = Column(String, ForeignKey("company_status.code"), index=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ReportTypes(Base):
    __tablename__ = "report_types"
    
    id = Column(Integer, primary_key=True)
    code = column(String, unique=True)
    name = Column(String, unique=True)

class LetterTypes(Base):
    __tablename__ = "letter_types"
    
    id = Column(Integer, primary_key=True)
    code = column(String, unique=True)
    name = Column(String, unique=True)


class Auditors(Base):
    __tablename__ = "auditors"
    
    id = Column(Integer, primary_key=True)
    code = column(String, unique=True)
    name = Column(String, unique=True)