import sys
import json
from urllib.request import urlopen

import requests
import pandas as pd
import asyncio

try:
    import nest_asyncio
except ImportError:
    nest_asyncio = None

GET_HEADERS_REQUEST = {
    'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/111.0.0.0 '
        'Safari/537.36'
}


def get_dict_from_xml_api(url: str):
    try:
        with urlopen(url) as file:
            string_json = file.read().decode('utf-8')

        return json.loads(string_json)
    except ConnectionError:
        print("fall back to manual mode")
        pass
    except Exception as e:
        print(e.__context__)
        pass


def get_data_from_cdn_tsetmec_api(data: str, code: str, date: str):
    url = f'http://cdn.tsetmc.com/api/{data}/{code}/{date}'
    response = requests.get(url=url, cookies={}, headers=GET_HEADERS_REQUEST)

    return response.json()


def get_csv_from_github(name):
    url = f"https://raw.githubusercontent.com/mohsenebrahimyir/codal-tsetmc/master/data/{name}.csv"
    df = pd.read_csv(url)
    return df


def get_results_by_asyncio_loop(tasks):
    async def run_all():
        return await asyncio.gather(*tasks)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if sys.platform == "win32":
            if isinstance(loop, asyncio.SelectorEventLoop):
                loop = asyncio.ProactorEventLoop()
                asyncio.set_event_loop(loop)

        if loop.is_running():
            if nest_asyncio:
                nest_asyncio.apply()
                return loop.run_until_complete(run_all())
            else:
                raise RuntimeError(
                    "Event loop is running and nest_asyncio is not available."
                )

        return loop.run_until_complete(run_all())

    except RuntimeError:
        # fallback در صورت بسته بودن یا مشکل در حلقه قبلی
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        return new_loop.run_until_complete(run_all())

    except Exception as e:
        print("Async loop error:", e.__context__ or e)
