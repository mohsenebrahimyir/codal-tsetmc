import numpy as np
import pandas as pd
# noinspection PyUnresolvedReferences
import jalali_pandas
from codal_tsetmc.config.engine import (
    Column, Integer, String, Base, session
)
from codal_tsetmc.tools.database import read_table_by_conditions
from sqlalchemy import BigInteger


def add_event(df, event, ratio):
    df = df.merge(event[["date", ratio]], how="outer", on="date")
    df = df.sort_values("date").reset_index(drop=True)
    df[ratio] = df[ratio].fillna(method="ffill")
    df = df.dropna(subset=['close'])
    df["cumulative"] = df[ratio].fillna(1).cumprod()

    df[ratio + "_ratio"] = df.cumulative / df.cumulative.iloc[-1]
    return df.drop('cumulative', axis=1)


class Stock(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    name = Column(String)
    name_en = Column(String)
    isin = Column(String)
    code = Column(BigInteger, unique=True)
    capital = Column(BigInteger)
    instrument_code = Column(BigInteger)
    instrument_id = Column(String)
    group_name = Column(String)
    group_code = Column(Integer)
    group_type = Column(String)
    market_name = Column(String)
    market_code = Column(String)
    market_type = Column(String)

    _price_cached = False
    _price_counter = 0
    _prices_cached = False
    _prices_counter = 0
    _capital_cached = False
    _capital_counter = 0
    _capitals_cached = False
    _capitals_counter = 0
    _market_cached = False
    _market_counter = 0
    _dollar_cached = False
    _dollar_counter = 0
    _index_cached = False
    _index_counter = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._price = None
        self._prices = None
        self._capital = None
        self._capitals = None
        self._market = None
        self._index = None
        self._dollar = None

    @property
    def price(self) -> pd.DataFrame:
        self._price_counter += 1
        if self._price_cached:
            return self._price

        from codal_tsetmc import StockPrice
        df = read_table_by_conditions(StockPrice.__tablename__, "code", self.code)
        if df.empty:
            self._price_cached = True
            self._price = df
            return self._price

        self._price_cached = True
        self._price = df[(df["date"] == max(df["date"]))].iloc[0].price

        return self._price

    @property
    def prices(self) -> pd.DataFrame:
        self._prices_counter += 1
        if self._prices_cached:
            return self._prices

        from codal_tsetmc import StockPrice
        df = read_table_by_conditions(StockPrice.__tablename__, "code", self.code)
        if df.empty:
            self._prices_cached = True
            self._prices = df
            return self._prices

        df["jdate"] = df["date"].replace(regex={"000000$": ""})
        df["date"] = df["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        df.set_index("date", inplace=True)
        self._prices_cached = True
        self._prices = df[[
            "jdate", "symbol", "code", "price", "value", "volume"
        ]].dropna()

        return self._prices

    @property
    def cap(self) -> pd.DataFrame:
        self._capital_counter += 1
        if self._capital_cached:
            return self._capital

        from codal_tsetmc import StockCapital
        df = read_table_by_conditions(StockCapital.__tablename__, "code", self.code)
        if df.empty:
            self._capital_cached = True
            self._capital = df
            return self._capital

        self._capital_cached = True
        self._capital = df[(df["date"] == max(df["date"]))].iloc[0].new

        return self._capital

    @property
    def capitals(self) -> pd.DataFrame:
        self._capitals_counter += 1
        if self._capitals_cached:
            return self._prices

        from codal_tsetmc import StockCapital
        df = read_table_by_conditions(StockCapital.__tablename__, "code", self.code)
        if df.empty:
            self._capitals_cached = True
            self._prices = df
            return self._prices

        df["jdate"] = df["date"].replace(regex={"000000$": ""})
        df["date"] = df["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        df.set_index("date", inplace=True)
        self._capitals_cached = True
        self._capitals = df[[
            "jdate", "symbol", "code", "old", "new"
        ]].dropna()

        return self._capitals

    @property
    def market(self) -> pd.DataFrame:
        self._market_counter += 1
        if self._market_cached:
            return self._market

        df = self.prices
        if df.empty:
            self._market_cached = True
            self._market = df
            return self._market

        from codal_tsetmc import StockCapital
        capitals = read_table_by_conditions(
            StockCapital.__tablename__,
            "code",
            self.code
        ).rename(columns={"new": "capital"})
        capitals["date"] = capitals["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        capitals.set_index("date", inplace=True)

        df = df.join(capitals[["capital"]], how="outer").sort_index()

        if capitals.empty:
            df["capital"].iat[0] = self.capital
        else:
            df["capital"].iat[0] = capitals["old"].iloc[0]

        df["capital"] = df["capital"].ffill()
        df["market"] = df["capital"] * df["price"]
        self._market_cached = True
        self._market = df[["jdate", "symbol", "code", "capital", "market", "value"]].dropna()

        return self._market

    @property
    def index(self) -> pd.DataFrame:
        self._index_counter += 1
        if self._index_cached:
            return self._index

        df = self.market
        if df.empty:
            self._index_cached = True
            self._index = df
            return self._index

        from codal_tsetmc import StockPrice
        index = read_table_by_conditions(
            StockPrice.__tablename__,
            "code",
            "32097828799138957"
        ).rename(columns={"price": "index"})
        index["date"] = index["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        index.set_index("date", inplace=True)
        df = df.join(index[["index"]], how="outer")
        df["jdate"] = df["jdate"].ffill()
        df["symbol"] = df["symbol"].ffill()
        df["market"] = df["market"].ffill()
        self._index_cached = True
        self._index = df[["jdate", "symbol", "market", "index"]].dropna()

        return self._index

    def beta(self, during=3650):
        df = self.index[["market", "index"]][-during:].pct_change().dropna()
        return np.cov(df["market"], df["index"])[0, 1] / np.var(df["index"])

    def update_price(self):
        from codal_tsetmc.download.tsetmc.price import update_stock_prices

        try:
            return update_stock_prices(self.code)
        except Exception as e:
            print(e)
            return False

    def update_capital(self):
        from codal_tsetmc.download.tsetmc.capital import update_stock_capitals

        try:
            return update_stock_capitals(self.code)
        except Exception as e:
            print(e)
            return False

    def __repr__(self):
        return f"symbol: {self.symbol}, "\
               f"code: {self.code}, "\
               f"name: {self.name}, "\
               f"group: {self.group_name}"

    def __str__(self):
        return f"symbol: {self.symbol}, "\
               f"code: {self.code}, "\
               f"name: {self.name}, "\
               f"group: {self.group_name}"

    @staticmethod
    def get_group():
        return (
            session.query(Stock.group_code, Stock.group_name)
            .group_by(Stock.group_code)
            .all()
        )


def get_asset(name):
    name = name.replace("ی", "ي").replace("ک", "ك")
    return Stock.query.filter_by(name=name).first()
