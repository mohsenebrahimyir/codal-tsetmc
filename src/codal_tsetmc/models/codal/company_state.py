from codal_tsetmc.config.engine import Base
from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import relationship


class CompanyState(Base):
    __tablename__ = "company_state"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)

    linked_companies = relationship("Company", backref="state")

    def __repr__(self):
        return f"({self.code}, {self.title})"

