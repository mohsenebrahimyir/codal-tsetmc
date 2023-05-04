from codal_tsetmc.config import *
from sqlalchemy.orm import relationship
import pandas as pd
import requests
import jalali_pandas
from codal_tsetmc.tools.string_edit import shamsi_to_yyyymmdd
from codal_tsetmc.download.price import update_list_of_stocks_price


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
    isin = Column(String)
    code = Column(String, unique=True)
    last_capital = Column(BIGINT)
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
    _df_cached = False
    _price_cached = False
    _dollar_cached = False
    _capital_cached = False
    _df_counter = 0
    _price_counter = 0
    _dollar_counter = 0
    _capital_counter = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def df(self) -> pd.DataFrame:
        """dataframe of stock price with date and OHLC"""
        self._df_counter += 1
        if self._df_cached:
            return self._df
        
        query = f"select * from stock_price where code = '{self.code}'"
        df = pd.read_sql(query, engine)

        if df.empty:
            self._df_cached = True
            self._df = df
            return self._df
        
        df["symbol"] = self.symbol
        df = df.sort_values("date")
        df.reset_index(drop=True, inplace=True)
        self._df_cached = True
        self._df = df[["date", "code", "symbol", "price"]]

        return self._df

    @property
    def price(self) -> pd.DataFrame:
        self._price_counter += 1
        if self._price_cached:
            return self._price

        df = self.df

        if df.empty:
            self._price_cached = True
            self._price = df
            return self._price

        capital_query = f"select * from stock_capital where code = '{self.code}'"
        capital = pd.read_sql(capital_query, engine)
        if capital is not None:

            df["date"] = pd.to_datetime(df["dtyyyymmdd"], format="%Y%m%d")
            df.set_index("date", inplace=True)
            df = df[["jdate", "volume", "value", "capital"]]
            self._price_cached = True
            self._price = df

        return self._price

    @property
    def dollar(self) -> pd.DataFrame:
        """dataframe of stock dollar with date and close"""
        self._dollar_counter += 1
        if self._dollar_cached:
            return self._dollar

        df = self.price

        if df.empty:
            self._dollar_cached = True
            self._dollar = df
            return self._dollar

        query = f"select * from commodity_price where symbol = 'price_dollar_rl'"
        dollar = pd.read_sql(query, engine)
        dollar["date"] = pd.to_datetime(dollar["date"], format="%Y%m%d")
        dollar = dollar.set_index("date").rename(columns={"close": "dollar"})
        df = df.merge(dollar[["dollar"]], how="outer", on="date")
        df["dollar"] = df["dollar"].fillna(method="ffill")
        df["value"] = df["value"] / df["dollar"]
        df = df[["jdate", "volume", "value", "capital"]].dropna(subset=['close'])

        self._dollar_cached = True
        self._dollar = df

        return self._dollar

    def update_price(self):

        try:
            return update_list_of_stocks_price([self.code])
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
    ticker = Column(String)
    date = Column(String)
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

def get_asset(name):
    name = name.replace("ی", "ي").replace("ک", "ك")
    return Stocks.query.filter_by(name=name).first()
