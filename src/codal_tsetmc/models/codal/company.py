from sqlalchemy import Integer, Column, String
from ...config.engine import Base


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    name = Column(String)
    isic = Column(String)
    type = Column(Integer)
    status = Column(Integer)
    industry = Column(Integer)
    nature = Column(Integer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"({self.symbol}, "\
               f"{self.name}, "
