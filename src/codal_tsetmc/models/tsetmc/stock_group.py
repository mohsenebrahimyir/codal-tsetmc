from codal_tsetmc.config.engine import (
    Column, Integer, String, Base
)


class StockGroup(Base):
    __tablename__ = "stock_group"

    id = Column(Integer, primary_key=True)
    code = Column(Integer, unique=True)
    name = Column(String)
    type = Column(String)
    description = Column(String)

    def __repr__(self):
        return f"(group: {self.name}, code: {self.code}), type: {self.type}"
