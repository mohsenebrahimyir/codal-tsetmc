import re
from jdatetime import date as jd
from jdatetime import datetime as jdt


FA_TO_EN_DIGITS = {
    "۱": "1",
    "۲": "2",
    "۳": "3",
    "۴": "4",
    "۵": "5",
    "۶": "6",
    "۷": "7",
    "۸": "8",
    "۹": "9",
    "۰": "0"
}

REPLACE_INCORRECT_CHARS = {
    "ي": "ی",
    "ى": "ی",
    "ك": "ک",
    r"[\u200c\u200f\u200e\u200d\u202a-\u202e]": " ",  # all space chars
    r"\xa0": " ",  # Non-breaking space
    r"\s*،\s*": "، ",
    r"\s*\)\s*": ") ",
    r"\s*\(\s*": " (",
    r"\s*–\s*": " - ",
    r"\s*-\s*": " - ",
    r"\s+": " ",  # Replace multiple spaces with a single space
    r"^\s+": "",  # Remove space in first char
    r"\s+$": ""  # Remove space in last char
}

EMPTY_TO_NONE = {
    "^$": None,
    "^--$": None
}


def replace_all(text, dic):
    text = str(text)
    for k, v in dic.items():
        text = re.sub(k, v, text)

    return text


def digit_string_to_integer(string: str | None) -> int | None:
    try:
        if not string:
            return None
        s = replace_all(string, {"[^0-9]": ""})
        return int(s) if s else None
    except ValueError:
        return None


def string_to_num(string: str | None, digit: int = 14) -> float | None:
    if not string:
        return None
    s = replace_all(string, {"[^0-9]": ""})
    return int(s) * 10 ** (digit - len(s))


def datetime_to_num(dt: str) -> int:
    n = string_to_num(dt, 14)
    return int(n) if n else 0


def date_to_num(d: str):
    n = string_to_num(d, 8)
    return int(n) if n else 0


def num_to_datetime(num, datetime=True, d: str = "/", t: str = ":", sep: str = " "):
    _n = str(num)
    if _n.__len__() < 8:
        _n += "0" * (8 - _n.__len__())

    date = f"{_n[0:4]}{d}{_n[4:6]}{d}{_n[6:8]}"
    if datetime:
        if _n.__len__() < 14:
            _n += "0" * (14 - _n.__len__())
        time = f"{_n[8:10]}{t}{_n[10:12]}{t}{_n[12:14]}"
        return f"{date}{sep}{time}"

    return date


def num_to_date(num, d: str = "/"):
    return num_to_datetime(num, datetime=False, d=d)


def yyyymmdd_to_shamsi(date):
    date = str(date)
    return jd.fromgregorian(
        day=int(date[-2:]), month=int(date[4:6]), year=int(date[:4])
    ).strftime("%Y/%m/%d")


def shamsi_to_yyyymmdd(date: str):
    jdt.strptime(date, "%Y%m%d%H%M%S").togregorian().strftime("%Y%m%d")


def remove_key(d, key):
    r = dict(d)
    del r[key]
    return r


def value_to_float(x):
    x = x.replace(",", "")
    if type(x) is float or type(x) is int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace(' K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace(' M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace(' B', '')) * 1000000000
    return 0.0


def to_snake_case(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def df_col_to_snake_case(df):
    df.columns = map(to_snake_case, df.columns)
    return df
