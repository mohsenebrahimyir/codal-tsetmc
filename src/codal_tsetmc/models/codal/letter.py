from codal_tsetmc.config.engine import Base
from sqlalchemy import Integer, Column, BigInteger, String, ForeignKey


class Letter(Base):
    __tablename__ = "letter"

    id = Column(Integer, primary_key=True)
    publish_date_time = Column(BigInteger)
    sent_date_time = Column(BigInteger)
    tracing_no = Column(BigInteger, unique=True)
    letter_serial = Column(String, unique=True)
    letter_title = Column(String)
    letter_code = Column(String)
    letter_types = Column(String)
    symbol = Column(String, ForeignKey("company.symbol"))
    name = Column(String)

    def __repr__(self):
        return f"tracing_no: {self.tracing_no}, "\
               f"serial: {self.letter_serial}"
