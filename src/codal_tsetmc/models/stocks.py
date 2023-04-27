from codal_tsetmc.config import *
from sqlalchemy.orm import relationship
import pandas as pd
import requests
import jalali_pandas


def add_event(df, event, ratio):
    df = df.merge(event[["dtyyyymmdd", ratio]], how="outer", on="dtyyyymmdd")
    df = df.sort_values("dtyyyymmdd").reset_index(drop=True)

    if ratio == "dividend":
        df[ratio] = df[ratio].shift(-1)
        df = df.dropna(subset=['close'])
        df["cumulative"] = (
            (df["close"] - df[ratio].fillna(0))/df["close"]
        ).cumprod()
    elif ratio == "capital":
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
    _df_cached = False
    _price_cached = False
    _dollar_cached = False
    _client_cached = False
    _df_counter = 0
    _price_counter = 0
    _dollar_counter = 0

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
        df["date"] = pd.to_datetime(df["dtyyyymmdd"], format="%Y%m%d")
        df["jdate"] = df.date.jalali.to_jalali()
        df = df.sort_values("date")
        df.reset_index(drop=True, inplace=True)
        df.set_index("date", inplace=True)
        self._df_cached = True
        self._df = df

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

        df = df.rename(columns={"vol": "volume"})

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
        dollar["date"] = pd.to_datetime(dollar["dtyyyymmdd"], format="%Y%m%d")
        dollar = dollar.set_index("date").rename(columns={"close": "dollar"})
        df = df.merge(dollar[["dollar"]], how="outer", on="date")
        df["dollar"] = df["dollar"].fillna(method="ffill")
        df["value"] = df["value"] / df["dollar"]
        df = df[["jdate", "volume", "value", "capital", "value"]].dropna(subset=['close'])

        self._dollar_cached = True
        self._dollar = df

        return self._dollar

    def update_price(self):
        from codal_tsetmc.download import update_stock_price

        try:
            return update_stock_price(self.code)
        except:
            return False

    def summary(self):
        """summart of stock"""
        df = self.df
        sdate = df.index.min().strftime("%Y/%m/%d")
        edate = df.index.max().strftime("%Y/%m/%d")

        print(f"Start date: {sdate}")
        print(f"End date: {edate}")
        print(f"Total days: {len(df)}")

    def get_instant_detail(self) -> dict:
        url = (
            f"http://www.tsetmc.com/tsev2/data/instinfodata.aspx?i={self.code}&c=27%20"
        )
        headers = {
            "Connection": "keep-alive",
            "Accept": "text/plain, */*; q=0.01",
            "DNT": "1",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
        }
        # 12:29:40,A ,4300,4364,4577,4361,4577,4250,195,702025,3070743824,0,20220326,122940;
        r = requests.get(url, headers=headers)
        main_response = r.text.split(";")[0]
        main_response = main_response.split(",")

        self.time = main_response[0]
        self.last_price = main_response[2]
        self.last_close = main_response[3]
        self.last_high = main_response[4]
        self.last_low = main_response[5]
        self.last_open = main_response[6]
        self.trade_count = main_response[7]
        self.trade_volume = main_response[8]
        self.trade_value = main_response[9]
        self.market_cap = main_response[10]
        self.date_string = main_response[12]
        self.time_string = main_response[13]
        del main_response[11]
        del main_response[1]

        keys = [
            "time",
            "last_price",
            "last_close",
            "last_high",
            "last_low",
            "last_open",
            "trade_count",
            "trade_volume",
            "trade_value",
            "market_cap",
            "date_string",
            "time_string",
        ]
        return dict(zip(keys, main_response))

    def __repr__(self):
        return f"{self.title}-{self.name}-{self.group_name}"

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
    date = Column("dtyyyymmdd", Integer, index=True)
    date_shamsi = Column(String)
    close = Column(Float)
    value = Column(BIGINT)
    volome = Column(BIGINT)
    per = Column(String)

    def __repr__(self):
        return f"({self.stock.name}, {self.date}, {self.close:.0f})"


class StockCapital(Base):
    __tablename__ = "stock_capital"

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("stocks.code"), index=True)
    date = Column("dtyyyymmdd", Integer, index=True)
    capital = Column(BIGINT)

    def __repr__(self):
        return f"{self.stock.name}, {self.date}, {self.new_capital/self.old_capital*100:.2f}"

def get_asset(name):
    name = name.replace("ی", "ي").replace("ک", "ك")
    return Stocks.query.filter_by(name=name).first()
