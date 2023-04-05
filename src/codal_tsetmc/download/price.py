from jdatetime import date as jdate
from datetime import datetime
import asyncio
import aiohttp
import pandas as pd
import requests
import io
import json
import requests

import codal_tsetmc.config as db
from codal_tsetmc.models import StockPrice, Stocks


def convert_to_shamsi(date):
    date = str(date)
    return jdate.fromgregorian(
        day=int(date[-2:]), month=int(date[4:6]), year=int(date[:4])
    ).strftime("%Y/%m/%d")


def get_stock_price_history(stock_id: str) -> pd.DataFrame:
    """Get stock price history from the web.

    params:
    ----------------
    stock_id: int
        http://www.tsetmc.com/Loader.aspx?ParTree=151311&i=**35700344742885862#**
        number after i=

    return:
    ----------------
    pd.DataFrame
        date: str
        open: float
        high: float
        low: float
        close: float
        volume: int

    example
    ----------------
    df = get_stock_price_history("35700344742885862")
    """
    now = datetime.now().strftime("%Y%m%d")
    url = f"http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={stock_id}&DateFrom=20000101&DateTo={now}&b=0"
    s = requests.get(url).content
    df = pd.read_csv(io.StringIO(s.decode("utf-8")))
    df.columns = [i[1:-1].lower() for i in df.columns]
    return df


async def update_stock_price(code: str):
    """
    Update (or download for the first time) Stock prices


    params:
    ----------------
    code: str or intege

    example
    ----------------
    `update_stock_price('44891482026867833') #Done`
    or use inside Stock object
    ```
    from codal_tsetmc.models import Stocks
    stock = Stocks.query.first()
    stock.update() #Done
    """
    try:
        now = datetime.now().strftime("%Y%m%d")
        try:
            max_date_query = (
                f"select max(dtyyyymmdd) as date from stock_price where code = '{code}'"
            )
            max_date = pd.read_sql(max_date_query, db.engine)
            last_date = max_date.date.iat[0]
        except Exception as e:
            last_date = None
        try:
            if last_date is None:  # no any record added in database
                url = f"http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={code}&DateFrom=20000101&DateTo={now}&b=0"
            elif str(last_date) < now:  # need to updata new price data
                url = f"http://www.tsetmc.com/tse/data/Export-txt.aspx?a=InsTrade&InsCode={code}&DateFrom={str(last_date)}&DateTo={now}&b=0"
            else:  # The price data for this code is updateed
                return
        except Exception as e:
            print(f"Error on formating price:{str(e)}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.text()
        df = pd.read_csv(io.StringIO(data))
        df.columns = [i[1:-1].lower() for i in df.columns]
        df["code"] = code
        df["date_shamsi"] = df["dtyyyymmdd"].apply(convert_to_shamsi)
        try:
            q = f"select dtyyyymmdd from stock_price where code = '{code}'"
            temp = pd.read_sql(q, db.engine)
            df = df[~df.dtyyyymmdd.isin(temp.dtyyyymmdd)]
        except:
            pass
        df.to_sql("stock_price", db.engine, if_exists="append", index=False)
        return True, code

    except Exception as e:
        return e, code


def update_group_price(code):
    """
    Update and download data of all stocks in  a group.\n

    `Warning: Stock table should be updated`
    """
    stocks = db.session.query(Stocks.code).filter_by(group_code=code).all()
    print("updating group", code, end="\r")
    loop = asyncio.get_event_loop()
    tasks = [update_stock_price(stock[0]) for stock in stocks]
    try:
        results = loop.run_until_complete(asyncio.gather(*tasks))
    except RuntimeError:
        WARNING_COLOR = "\033[93m"
        ENDING_COLOR = "\033[0m"
        print(WARNING_COLOR, "Please update stock table", ENDING_COLOR)
        print(
            f"{WARNING_COLOR}If you are using jupyter notebook, please run following command:{ENDING_COLOR}"
        )
        print("```")
        print("%pip install nest_asyncio")
        print("import nest_asyncio; nest_asyncio.apply()")
        print("from codal_tsetmc.download import get_all_price")
        print("get_all_price()")
        print("```")
        raise RuntimeError

    print("group", code, "updated", end="\r")
    return results


def get_all_price():
    codes = db.session.query(db.distinct(Stocks.group_code)).all()
    for i, code in enumerate(codes):
        print(
            f"{' '*18} total progress: {100*(i+1)/len(codes):.2f}%",
            end="\r",
        )
        update_group_price(code[0])

    print("Price Download Finished.", " "*20)



def get_data_from_cdn_tsetmec_api(data: str, code: str, date: str):
    url = f'http://cdn.tsetmc.com/api/{data}/{code}/{date}'
    cookies = {}

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    }
    response = requests.get(
        url=url,
        cookies=cookies,
        headers=headers,
        verify=False
    )
    
    return json.loads(response.text)

def get_number_of_shares_daily(code: str, date: str):
    data = "Instrument/GetInstrumentHistory"
    dict_data = get_data_from_cdn_tsetmec_api(data, code, date)
    return dict_data["instrumentHistory"]["zTitad"]

def get_closing_price_daily(code: str, date: str):
    data = "ClosingPrice/GetClosingPriceDaily"
    dict_data = get_data_from_cdn_tsetmec_api(data, code, date)
    
    return dict_data["closingPriceDaily"]["pClosing"]

def get_market_value(code, date):
    share = get_number_of_shares_daily(code, date)
    price = get_closing_price_daily(code, date)

    return price * share
