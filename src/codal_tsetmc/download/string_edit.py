import re
import pandas as pd

FA_TO_EN_DIGITS = {
    "۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5",
    "۶": "6", "۷": "7", "۸": "8", "۹": "9", "۰": "0",
}

REMOVE_COMMA_AND_ADD_MINUS_SIGN = {
    "\,|\)": "",
    "\(": "-"
}

FIX_DIGITS = {**FA_TO_EN_DIGITS, **REMOVE_COMMA_AND_ADD_MINUS_SIGN}

def to_snake_case(name):
    #TODO: ...
    """_summary_

    Args:
        name (_type_): _description_

    Returns:
        _type_: _description_
    """
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()


def df_col_to_snake_case(df):
    #TODO: ...
    """_summary_

    Args:
        d (_type_): _description_

    Returns:
        _type_: _description_
    """
    df.columns = map(to_snake_case, df.columns)
    return df
