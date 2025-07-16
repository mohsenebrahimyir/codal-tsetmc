from sqlalchemy import Integer, Column, BigInteger, String, Boolean
from ...config.engine import Base


class Letter(Base):
    __tablename__ = "letter"

    id = Column(String, primary_key=True)
    publish_date_time = Column(BigInteger, nullable=False)
    sent_date_time = Column(BigInteger, nullable=False)
    tracing_no = Column(Integer)
    title = Column(String)
    code = Column(String)
    type = Column(String)
    symbol = Column(String)
    company_name = Column(String)
    has_html = Column(Boolean)
    has_pdf = Column(Boolean)
    has_excel = Column(Boolean)
    has_xbrl = Column(Boolean)
    has_attachment = Column(Boolean)

    def __repr__(self):
        return f"{self.id} ({self.title})"
