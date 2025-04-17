from codal_tsetmc.config.engine import Base
from sqlalchemy import Integer, Column, String


class CompanyType(Base):
    __tablename__ = "company_type"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.title})"

