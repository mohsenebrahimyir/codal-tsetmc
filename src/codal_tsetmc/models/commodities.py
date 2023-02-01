from codal_tsetmc.config import *
from sqlalchemy.orm import relationship
import pandas as pd


class CommodityPrice(Base):
    __tablename__ = "commodity_price"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    date = Column("dtyyyymmdd", Integer, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

    def __repr__(self):
        #TODO: add symbol to reper
        return f"قیمت کامودیتی"
