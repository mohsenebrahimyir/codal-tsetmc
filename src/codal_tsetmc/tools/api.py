import json
from urllib.request import urlopen
import requests
import pandas as pd

import asyncio
import aiohttp

def get_dict_from_xml_api(url: str) -> dict:
 
    try:
        with urlopen(url) as file:
            string_json = file.read().decode('utf-8')
    except ConnectionError:
        print("fall back to manual mode")
        pass
    except Exception as e:
        print(e)
        pass

    return json.loads(string_json)


def get_data_from_cdn_tsetmec_api(data: str, code: str, date: str):
    url = f'http://cdn.tsetmc.com/api/{data}/{code}/{date}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    }
    response = requests.get(url=url, cookies={}, headers=headers, verify=False)
    
    return response.json()


def get_rawdata_from_github(symbol):
    url = f"https://raw.githubusercontent.com/mohsenebrahimyir/codal-tsetmc/master/data/{symbol}.csv"
    df = pd.read_csv(url)
    return df


async def get_async_api(url) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response