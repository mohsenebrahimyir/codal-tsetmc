from codal_tsetmc.config.engine import Base
from sqlalchemy import Column, Integer, String


class ReportType(Base):
    __tablename__ = "report_type"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.title})"

