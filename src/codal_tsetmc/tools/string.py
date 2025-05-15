import re
from jdatetime import date as jd
from jdatetime import datetime as jdt

FA_TO_EN_DIGITS = {
    "۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5",
    "۶": "6", "۷": "7", "۸": "8", "۹": "9", "۰": "0"
}

AR_TO_FA_LETTER = {
    "ي": "ی",
    "ك": "ک"
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


def digit_string_to_integer(string: str) -> int | None:
    try:
        return int(string)
    except ValueError:
        return None


def datetime_to_num(dt):
    try:
        if dt == "" or dt is None:
            return None
        dt = replace_all(dt, {"[^0-9]": ""})
        return int(dt) * 10 ** (14 - len(dt))
    except Exception as e:
        print(e.__context__)

    return dt


def num_to_datetime(num, datetime=True, d="/", t=":", sep=" "):
    num = str(num)
    date = f"{num[0:4]}{d}{num[4:6]}{d}{num[6:8]}"
    time = f"{num[8:10]}{t}{num[10:12]}{t}{num[12:14]}"
    if datetime:
        return f"{date}{sep}{time}"
    else:
        return date


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
