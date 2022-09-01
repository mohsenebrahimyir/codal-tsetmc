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
        df[ratio] = df[ratio].shift(1)
        df = df.dropna(subset=['close'])
        df["cumulative"] = df[ratio].fillna(1).cumprod()

    df[ratio+"_ratio"] = df.cumulative/df.cumulative.iloc[-1]
    return df.drop('cumulative', axis=1)


class Stocks(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    title = Column(String)
    group_name = Column(String)
    group_code = Column(Integer)
    instId = Column(String)
    insCode = Column(String)
    code = Column(String, unique=True)
    sectorPe = Column(Float)
    shareCount = Column(Float)
    estimatedEps = Column(Float)
    baseVol = Column(Float)
    prices = relationship("StockPrice", backref="stock")
    clients = relationship("StockClient", backref="stock")
    dividends = relationship("StockDividend", backref="stock")
    capitals = relationship("StockCapital", backref="stock")
    adjusteds = relationship("StockAdjusted", backref="stock")
    _cached = False
    _price_cached = False
    _client_cached = False
    _capital_cached = False
    _dividend_cached = False
    _adjusted_cached = False
    _df_counter = 0
    _price_counter = 0
    _client_counter = 0
    _capital_counter = 0
    _dividend_counter = 0
    _adjusted_counter = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symbol = self.name

    @property
    def df(self) -> pd.DataFrame:
        """dataframe of stock price with date and OHLC"""
        self._df_counter += 1
        if self._cached:
            return self._df
        query = f"select * from stock_price where code = '{self.code}'"
        df = pd.read_sql(query, engine)
        if df.empty:
            self._cached = True
            self._df = df
            return self._df
        df["date"] = pd.to_datetime(df["dtyyyymmdd"], format="%Y%m%d")
        df["jdate"] = df.date.jalali.to_jalali()
        df = df.sort_values("date")
        df.reset_index(drop=True, inplace=True)
        df.set_index("date", inplace=True)
        self._cached = True
        self._df = df

        return self._df

    @property
    def price(self) -> pd.DataFrame:
        """dataframe of stock price with date and OHLC"""
        self._price_counter += 1
        if self._price_cached:
            return self._price

        df = self.df.join(self.client["natural"]).fillna(0)
        if df.empty:
            self._price_cached = True
            self._price = df
            return self._price
        
        df = df.rename(columns={"vol": "volume"})

        try:
            df = add_event(df, self.dividend, "dividend")
            df["open"]    = df["open"]    / df["dividend_ratio"]
            df["high"]    = df["high"]    / df["dividend_ratio"]
            df["low"]     = df["low"]     / df["dividend_ratio"]
            df["close"]   = df["close"]   / df["dividend_ratio"]
        except:
            pass

        try:
            df = add_event(df, self.capital, "capital")
            df["open"]    = df["open"]    / df["capital_ratio"]
            df["high"]    = df["high"]    / df["capital_ratio"]
            df["low"]     = df["low"]     / df["capital_ratio"]
            df["close"]   = df["close"]   / df["capital_ratio"]
            df["volume"]  = df["volume"]  * df["capital_ratio"]
            df["natural"] = df["natural"] * df["capital_ratio"]
        except:
            pass


        df["date"] = pd.to_datetime(df["dtyyyymmdd"], format="%Y%m%d")
        df.set_index("date", inplace=True)
        df = df[["jdate", "open", "high", "low", "close", "volume", "natural"]]

        self._price_cached = True
        self._price = df

        return self._price

    def update_price(self):
        from codal_tsetmc.download import update_stock_price

        try:
            return update_stock_price(self.code)
        except:
            return False

    @property
    def client(self) -> pd.DataFrame:
        """dataframe of stock client with date"""
        self._client_counter += 1
        if self._client_cached:
            return self._client
        query = f"select * from stock_client where code = '{self.code}'"
        df = pd.read_sql(query, engine)
        if df.empty:
            self._client_cached = True
            self._client = df
            return self._client

        df["date"] = pd.to_datetime(df["dtyyyymmdd"], format="%Y%m%d")
        df["jdate"] = df.date.jalali.to_jalali()
        df["natural"] = df["legal_sell_volume"] - df["legal_buy_volume"]
        df = df.sort_values("date")
        df.reset_index(drop=True, inplace=True)
        df.set_index("date", inplace=True)
        self._client_cached = True
        self._client = df

        return self._client

    def update_client(self):
        from codal_tsetmc.download import update_stock_client

        try:
            return update_stock_client(self.code)
        except:
            return False

    @property
    def dividend(self) -> pd.DataFrame:
        """dataframe of stock dividend with date"""
        self._dividend_counter += 1
        if self._dividend_cached:
            return self._dividend
        query = f"select * from stock_dividend where code = '{self.code}'"
        df = pd.read_sql(query, engine)
        if df.empty:
            self._dividend_cached = True
            self._dividend = df
            return self._dividend

        df["date"] = pd.to_datetime(df["dtyyyymmdd"], format="%Y%m%d")
        df["jdate"] = df.date.jalali.to_jalali()
        df = df.sort_values("date")
        df.reset_index(drop=True, inplace=True)
        df.set_index("date", inplace=True)
        self._dividend_cached = True
        self._dividend = df

        return self._dividend

    def update_dividend(self):
        from codal_tsetmc.download import update_stock_dividend

        try:
            return update_stock_dividend(self.code)
        except:
            return False

    @property
    def capital(self) -> pd.DataFrame:
        """dataframe of stock capital with date"""
        self._capital_counter += 1
        if self._capital_cached:
            return self._capital
        query = f"select * from stock_capital where code = '{self.code}'"
        df = pd.read_sql(query, engine)
        if df.empty:
            self._capital_cached = True
            self._capital = df
            return self._capital

        df["date"] = pd.to_datetime(df["dtyyyymmdd"], format="%Y%m%d")
        df["jdate"] = df.date.jalali.to_jalali()
        df["capital"] = df["old_capital"]/df["new_capital"]
        df = df.sort_values("date")
        df.reset_index(drop=True, inplace=True)
        df.set_index("date", inplace=True)
        self._capital_cached = True
        self._capital = df

        return self._capital

    def update_capital(self):
        from codal_tsetmc.download import update_stock_capital

        try:
            return update_stock_capital(self.code)
        except:
            return False

    @property
    def adjusted(self) -> pd.DataFrame:
        """dataframe of stock adjusted with date"""
        self._adjusted_counter += 1
        if self._adjusted_cached:
            return self._adjusted
        query = f"select * from stock_adjusted where code = '{self.code}'"
        df = pd.read_sql(query, engine)
        if df.empty:
            self._adjusted_cached = True
            self._adjusted = df
            return self._adjusted

        df["date"] = pd.to_datetime(df["dtyyyymmdd"], format="%Y%m%d")
        df["jdate"] = df.date.jalali.to_jalali()
        df["adjusted"] = df["old_price"]/df["new_price"]
        df = df.sort_values("date")
        df.reset_index(drop=True, inplace=True)
        df.set_index("date", inplace=True)
        self._adjusted_cached = True
        self._adjusted = df

        return self._adjusted

    def update_adjusted(self):
        from codal_tsetmc.download import update_stock_adjusted

        try:
            return update_stock_adjusted(self.code)
        except:
            return False

    @property
    def mpl(self):
        self._mpl = self.df.rename(
            columns={
                "close": "Close",
                "open": "Open",
                "high": "High",
                "low": "Low",
                "vol": "Volume",
            }
        )
        return self._mpl

    def summary(self):
        """summart of stock"""
        df = self.df
        sdate = df.index.min().strftime("%Y/%m/%d")
        edate = df.index.max().strftime("%Y/%m/%d")

        print(f"Start date: {sdate}")
        print(f"End date: {edate}")
        print(f"Total days: {len(df)}")

    def get_instant_detail(self) -> dict:
        """get instant detail of stock
        last_price, last_close, last_open, last_high, last_low, last_vol, trade_count, trade_value,market_cap
        instantly from the website

        Returns:
            dict: { last_price, last_close, last_open, last_high, last_low, last_vol, trade_count, trade_value,market_cap}
        """
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
    first = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    value = Column(BIGINT)
    vol = Column(BIGINT)
    openint = Column(Integer)
    per = Column(String)
    open = Column(Float)
    last = Column(Float)

    def __repr__(self):
        return f"{self.stock.name}, {self.date}, {self.close:.0f}"


class StockClient(Base):
    __tablename__ = "stock_client"

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("stocks.code"), index=True)
    date = Column("dtyyyymmdd", Integer, index=True)
    natural_buy_count = Column(Integer)
    legal_buy_count = Column(Integer)
    natural_sell_count = Column(Integer)
    legal_sell_count = Column(Integer)
    natural_buy_volume = Column(BIGINT)
    legal_buy_volume = Column(BIGINT)
    natural_sell_volume = Column(BIGINT)
    legal_sell_volume = Column(BIGINT)
    natural_buy_value = Column(BIGINT)
    legal_buy_value = Column(BIGINT)
    natural_sell_value = Column(BIGINT)
    legal_sell_value = Column(BIGINT)

    def change_of_ownership(self):
        return self.legal_sell_volume - self.legal_buy_volume

    def __repr__(self):
        return f"{self.stock.name}, {self.date}, {self.change_of_ownership()}"


class StockDividend(Base):
    __tablename__ = "stock_dividend"

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("stocks.code"), index=True)
    date = Column("dtyyyymmdd", Integer, index=True)
    dividend = Column(Float)

    def __repr__(self):
        return f"{self.stock.name}, {self.date}, {self.dividend}"


class StockCapital(Base):
    __tablename__ = "stock_capital"

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("stocks.code"), index=True)
    date = Column("dtyyyymmdd", Integer, index=True)
    old_capital = Column(BIGINT)
    new_capital = Column(BIGINT)

    def __repr__(self):
        return f"{self.stock.name}, {self.date}, {self.new_capital/self.old_capital*100:.2f}"


class StockAdjusted(Base):
    __tablename__ = "stock_adjusted"

    id = Column(Integer, primary_key=True)
    code = Column(String, ForeignKey("stocks.code"), index=True)
    date = Column("dtyyyymmdd", Integer, index=True)
    old_price = Column(Float)
    new_price = Column(Float)

    def __repr__(self):
        return f"{self.stock.name}, {self.date}, {self.new_price/self.old_price*100:.2f}"


def get_asset(name):
    name = name.replace("ی", "ي").replace("ک", "ك")
    return Stocks.query.filter_by(name=name).first()
