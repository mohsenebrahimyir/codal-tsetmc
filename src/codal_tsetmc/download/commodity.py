from datetime import datetime
import asyncio
import aiohttp
import pandas as pd
import numpy as np
import requests
import io

import codal_tsetmc.config as db
from codal_tsetmc.tools import fill_table_of_db_with_df

def get_commodity_price_history(symbol: str) -> pd.DataFrame:
    #TODO: ...
    """_summary_

    Returns:
        _type_: _description_
    """
    url = f"https://api.tgju.org/v1/market/indicator/summary-table-data/{symbol}"
    response = requests.get(url, params=[], headers={})
    res_dict = response.json()['data']
    df = pd.DataFrame.from_records(res_dict)
    df.columns = [
        'open', 'low',
        'high', 'close',
        'change_amount',
        'change_percent',
        'date', 'jdate'
    ]
    df['dtyyyymmdd'] = pd.to_numeric(df['date'].str.replace("/", ""))
    df['date'] = pd.to_datetime(df['date'])
    for column in ['open', 'low', 'high', 'close']:
        df[column] = pd.to_numeric(df[column].str.replace(",", ""))
    
    df["symbol"] = symbol

    return df[['symbol', 'dtyyyymmdd', 'open', 'low', 'high', 'close']]


def fill_commodity_price_table():
    #TODO
    """_summary_

    Returns:
        _type_: _description_
    """
    symbols = ["price_dollar_rl", "ons", "bourse"]
    for symbol in symbols:
        df = get_commodity_price_history(symbol)
        fill_table_of_db_with_df(df, "commodity_price", "dtyyyymmdd", f"where symbol = '{symbol}'")
