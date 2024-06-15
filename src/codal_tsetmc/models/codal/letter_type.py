from codal_tsetmc.config.engine import Base
from sqlalchemy import Column, Integer, String


class LetterType(Base):
    __tablename__ = "letter_type"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String, unique=True)

    def __repr__(self):
        return f"({self.code}, {self.title})"
