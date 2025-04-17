from codal_tsetmc.config.engine import Base
from sqlalchemy import Integer, Column, String


class CompanyState(Base):
    __tablename__ = "company_state"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.title})"

