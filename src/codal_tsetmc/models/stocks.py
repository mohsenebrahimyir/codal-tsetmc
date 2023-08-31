import numpy as np
import pandas as pd
import jalali_pandas
from sqlalchemy.orm import relationship

from codal_tsetmc.config.engine import (
    Column, Integer, String, BIGINT, Float, ForeignKey,
    Base, session
)
from codal_tsetmc.tools.database import read_table_by_conditions

def add_event(df, event, ratio):
    df = df.merge(event[["date", ratio]], how="outer", on="date")
    df = df.sort_values("date").reset_index(drop=True)
    df[ratio] = df[ratio].fillna(method="ffill")
    df = df.dropna(subset=['close'])
    df["cumulative"] = df[ratio].fillna(1).cumprod()

    df[ratio+"_ratio"] = df.cumulative/df.cumulative.iloc[-1]
    return df.drop('cumulative', axis=1)


class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    name = Column(String)
    name_en = Column(String)
    isin = Column(String)
    code = Column(String, unique=True)
    capital = Column(BIGINT)
    instrument_code = Column(String)
    instrument_id = Column(String)
    group_name = Column(String)
    group_code = Column(String)
    group_type = Column(String)
    market_name = Column(String)
    market_code = Column(String)
    market_type = Column(String)
    companies = relationship('Companies', backref='stock')
    prices = relationship("StockPrice", backref="stock")
    capitals = relationship("StockCapital", backref="stock")
    _price_cached = False
    _price_counter = 0
    _market_cached = False
    _market_counter = 0
    _dollar_cached = False
    _dollar_counter = 0
    _index_cached = False
    _index_counter = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @property
    def price(self) -> pd.DataFrame:
        """dataframe of stock price with date and OHLC"""
        self._price_counter += 1
        if self._price_cached:
            return self._price
        
        df = read_table_by_conditions("stock_price", "code", self.code)
        if df.empty:
            self._price_cached = True
            self._price = df
            return self._price
        
        df["jdate"] = df["date"].replace(regex={"000000$": ""})
        df["date"] = df["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        df.set_index("date", inplace=True)
        self._price_cached = True
        self._price = df[[
            "jdate", "ticker", "symbol", "code", "price", "value", "volume"
        ]].dropna()

        return self._price

    
    @property
    def market(self) -> pd.DataFrame:
        """dataframe of stock price with date and OHLC"""
        self._market_counter += 1
        if self._market_cached:
            return self._market
        
        df = self.price
        if df.empty:
            self._market_cached = True
            self._market = df
            return self._market

        capital = read_table_by_conditions("stock_capital", "code", self.code).rename(columns={"new": "capital"})
        capital["date"] = capital["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        capital.set_index("date", inplace=True)

        df = df.join(capital[["capital"]], how="outer").sort_index()

        if capital.empty:
            df["capital"].iat[0] = self.capital
        else:
            df["capital"].iat[0] = capital["old"].iloc[0]
        
        df["capital"] = df["capital"].ffill()
        df["market"]  = df["capital"] * df["price"]
        self._market_cached = True
        self._market = df[["jdate", "symbol", "market", "value"]].dropna()

        return self._market
    

    @property
    def dollar(self) -> pd.DataFrame:
        """dataframe of stock price with date and OHLC"""
        self._dollar_counter += 1
        if self._dollar_cached:
            return self._dollar
        
        df = self.market
        if df.empty:
            self._dollar_cached = True
            self._dollar = df
            return self._dollar

        dollar = read_table_by_conditions("commodity_price", "symbol", "price_dollar_rl").rename(columns={"price": "dollar"})
        dollar["date"] = dollar["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        dollar.set_index("date", inplace=True)
        df = df.join(dollar[["dollar"]], how="outer").sort_index()
        df["dollar"] = df["dollar"].ffill()
        df["market"] = df["market"] / df["dollar"]
        df["value"]  = df["value"]  / df["dollar"]
        self._dollar_cached = True
        self._dollar = df[["jdate", "symbol", "market", "value"]].dropna()

        return self._dollar


    @property
    def index(self) -> pd.DataFrame:
        """dataframe of stock price with date and OHLC"""
        self._index_counter += 1
        if self._index_cached:
            return self._index
        
        df = self.market
        if df.empty:
            self._index_cached = True
            self._index = df
            return self._index

        index = read_table_by_conditions("stock_price", "code", "32097828799138957").rename(columns={"price": "index"})
        index["date"] = index["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        index["index"] = index["index"] * 1_000_000_000
        index.set_index("date", inplace=True)
        df = df.join(index[["index"]], how="outer")
        df["jdate"]  = df["jdate"].ffill()
        df["symbol"] = df["symbol"].ffill()
        df["market"] = df["market"].ffill()
        self._index_cached = True
        self._index = df[["jdate", "symbol", "market", "index"]].dropna()

        return self._index
    
    def beta(self, during = 3650):
        df = self.index[["market", "index"]][-during:].pct_change().dropna()
        return np.cov(df["market"], df["index"])[0,1] / np.var(df["index"])


    def update_price(self):
        from codal_tsetmc.download.tsetmc.price import update_stocks_prices
        try:
            return update_stocks_prices([self.code])
        except:
            return False
    

    def update_capital(self):
        from codal_tsetmc.download.tsetmc.capital import update_stocks_capitals

        try:
            return update_stocks_capitals([self.code])
        except:
            return False

    def __repr__(self):
        return f"{self.symbol}-{self.name}-{self.group_name}"

    def __str__(self):
        return self.name

    @staticmethod
    def get_group():
        return (
            session.query(Stocks.group_code, Stocks.group_name)
            .group_by(Stocks.group_code)
            .all()
        )

class StockPrice(Base):
    __tablename__ = "stock_price"

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("stocks.code"), index=True)
    symbol = Column(String)
    ticker = Column(String)
    date = Column(String)
    volume = Column(BIGINT)
    value = Column(BIGINT)
    price = Column(Float)
    up_date = Column(String)

    def __repr__(self):
        return f"({self.stock.name}, {self.date}, {self.close:.0f})"


class StockCapital(Base):
    __tablename__ = "stock_capital"

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("stocks.code"), index=True)
    date = Column(String)
    old = Column(BIGINT)
    new = Column(BIGINT)
    up_date = Column(String)

    def __repr__(self):
        return f"{self.stock.name}, {max(self.date)}, {max(self.new)}"


class CommodityPrice(Base):
    __tablename__ = "commodity_price"

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    date = Column(String, index=True)
    price = Column(Float)
    up_date = Column(String)

    def __repr__(self):
        return f"قیمت کامودیتی {self.symbol}"


def get_asset(name):
    name = name.replace("ی", "ي").replace("ک", "ك")
    return Stocks.query.filter_by(name=name).first()
