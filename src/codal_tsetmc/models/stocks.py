from codal_tsetmc.config import *
from sqlalchemy.orm import relationship
import pandas as pd
import requests
import jalali_pandas


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
    _df_cached = False
    _df_counter = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def df(self) -> pd.DataFrame:
        """dataframe of stock price with date and OHLC"""
        self._df_counter += 1
        if self._df_cached:
            return self._df
        
        query = f"select * from stock_price where code = '{self.code}'"
        price = pd.read_sql(query, engine)
        price["jdate"] = price["date"].replace(regex={"000000$": ""})
        price["date"] = price["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        price.set_index("date", inplace=True)

        query = f"select * from stock_capital where code = '{self.code}'"
        capital = pd.read_sql(query, engine).rename(columns={"new": "capital"})
        capital["date"] = capital["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        capital.set_index("date", inplace=True)

        query = f"select * from stock_price where code = '32097828799138957'"
        index = pd.read_sql(query, engine).rename(columns={"price": "index"})
        index["date"] = index["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        index["index"] = index["index"] * 1_000_000_000
        index.set_index("date", inplace=True)

        query = f"select * from commodity_price where symbol = 'price_dollar_rl'"
        dollar = pd.read_sql(query, engine).rename(columns={"price": "dollar"})
        dollar["date"] = dollar["date"].jalali.parse_jalali("%Y%m%d%H%M%S").jalali.to_gregorian()
        dollar.set_index("date", inplace=True)

        if price.empty:
            self._df_cached = True
            self._df = price
            return self._df

        price["symbol"] = self.symbol
        df = price[["jdate", "ticker", "symbol", "code", "price"]].join(
                capital[["capital"]], how="outer"
            ).join(
                index[["index"]], how="outer"
            ).join(
                dollar[["dollar"]], how="outer"
            ).sort_index()
        
        if capital.empty:
            df["capital"].iat[0] = self.capital
        else:
            df["capital"].iat[0] = capital["old"].iloc[0]
        

        df["capital"] = df["capital"].ffill()
        df["ticker"]  = df["ticker"].ffill()
        df["symbol"]  = df["symbol"].ffill()
        df["price"]   = df["price"].ffill()
        df["code"]    = df["code"].ffill()
        df["index"]   = df["index"].ffill()
        df["dollar"]  = df["dollar"].ffill()

        df["market"]  = df["capital"] * df["price"]
        df["dollar"]  = df["market"] / df["dollar"]

        self._df_cached = True
        self._df = df.dropna()

        return self._df

    def update_price(self):
        from codal_tsetmc.download.tsetmc.price import update_stocks_prices

        try:
            return update_stocks_prices([self.code])
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
