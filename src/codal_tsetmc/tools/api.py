import sys
import json
from urllib.request import urlopen
import requests
import pandas as pd
import asyncio
import nest_asyncio


def get_dict_from_xml_api(url: str):
    try:
        with urlopen(url) as file:
            string_json = file.read().decode('utf-8')

        return json.loads(string_json)
    except ConnectionError:
        print("fall back to manual mode")
        pass
    except Exception as e:
        print("get_dict_from_xml_api: ", e.__context__, end='\r', flush=True)
        pass


def get_data_from_cdn_tsetmec_api(data: str, code: str, date: str):
    url = f'http://cdn.tsetmc.com/api/{data}/{code}/{date}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 '
                      'Safari/537.36'
    }
    response = requests.get(url=url, cookies={}, headers=headers) # , verify=False

    return response.json()


def get_csv_from_github(name):
    url = f"https://raw.githubusercontent.com/mohsenebrahimyir/codal-tsetmc/master/data/{name}.csv"
    df = pd.read_csv(url)
    return df


def get_results_by_asyncio_loop(tasks):
    nest_asyncio.apply()

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(asyncio.gather(*tasks))

    except Exception as e:
        print("get_results_by_asyncio_loop: ",  e.__context__, end='\r', flush=True)
