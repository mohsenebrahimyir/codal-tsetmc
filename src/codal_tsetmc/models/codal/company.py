from codal_tsetmc.config.engine import (
    Column, Integer, String, Base
)


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True)
    name = Column(String)
    isic = Column(Integer)
    type_code = Column(Integer)
    status_code = Column(Integer)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"({self.symbol}, "\
               f"{self.name}, "


