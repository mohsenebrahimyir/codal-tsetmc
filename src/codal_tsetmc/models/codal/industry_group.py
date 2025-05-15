from codal_tsetmc.config.engine import Base
from sqlalchemy import Integer, Column, String


class IndustryGroup(Base):
    __tablename__ = "industry_group"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    name = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.name})"
