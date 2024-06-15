from codal_tsetmc.config.engine import Base
from sqlalchemy import Column, Integer, String


class Auditor(Base):
    __tablename__ = "auditor"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    name = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.name})"
