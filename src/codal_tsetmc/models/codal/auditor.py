from sqlalchemy import Integer, Column, String
from ...config.engine import Base


class Auditor(Base):
    __tablename__ = "auditor"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True, nullable=False)
    title = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.title})"
