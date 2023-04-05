import json
from urllib.request import urlopen


def get_dict_from_xml_api(url: str) -> dict:
    print(f"Get data from {url}")
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