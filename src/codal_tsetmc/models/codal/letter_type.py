from sqlalchemy import Integer, Column, String
from ...config.engine import Base


class LetterType(Base):
    __tablename__ = "letter_type"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String, unique=True)

    def __repr__(self):
        return f"({self.code}, {self.title})"
