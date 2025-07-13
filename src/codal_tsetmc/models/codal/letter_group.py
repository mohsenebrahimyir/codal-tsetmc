from sqlalchemy import Integer, Column, String
from ...config.engine import Base


class LetterGroup(Base):
    __tablename__ = "letter_group"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    title = Column(String)

    def __repr__(self):
        return f"({self.code}, {self.title})"
