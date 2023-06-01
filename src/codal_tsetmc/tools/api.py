import json
from urllib.request import urlopen
import requests
import pandas as pd

def get_dict_from_xml_api(url: str):
 
    try:
        with urlopen(url) as file:
            string_json = file.read().decode('utf-8')
        
        return json.loads(string_json)
    except ConnectionError:
        print("fall back to manual mode")
        pass
    except Exception as e:
        print(e)
        pass


def get_data_from_cdn_tsetmec_api(data: str, code: str, date: str):
    url = f'http://cdn.tsetmc.com/api/{data}/{code}/{date}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    }
    response = requests.get(url=url, cookies={}, headers=headers, verify=False)
    
    return response.json()


def get_csv_from_github(name):
    url = f"https://raw.githubusercontent.com/mohsenebrahimyir/codal-tsetmc/master/data/{name}.csv"
    df = pd.read_csv(url)
    return df
