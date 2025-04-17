from codal_tsetmc.config.engine import Base
from sqlalchemy import Integer, Column, BigInteger, String


class Letter(Base):
    __tablename__ = "letter"

    id = Column(Integer, primary_key=True)
    publish_date_time = Column(BigInteger)
    sent_date_time = Column(BigInteger)
    tracing_no = Column(BigInteger, unique=True)
    serial = Column(String, unique=True)
    title = Column(String)
    code = Column(String)
    type = Column(String)
    symbol = Column(String)
    company_name = Column(String)

    def __repr__(self):
        return f"tracing_no: {self.tracing_no}, "\
               f"serial: {self.serial}"
