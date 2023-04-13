import re

FA_TO_EN_DIGITS = {
    "۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5",
    "۶": "6", "۷": "7", "۸": "8", "۹": "9", "۰": "0",
}

REMOVE_COMMA_AND_ADD_MINUS_SIGN = {
    "\,|\)": "",
    "\(": "-"
}

FIX_DIGITS = {**FA_TO_EN_DIGITS, **REMOVE_COMMA_AND_ADD_MINUS_SIGN}


TRANSLATE_FA_TO_EN = {
        "درآمدهای عملیاتی": "operating_revenue",
        "بهاى تمام شده درآمدهای عملیاتی": "cost_of_goods_sold",
        "سود (زيان) ناخالص": "gross_profit",
        "سود (زيان) عملياتي": "operating_profit",
        "هزينه‏‌هاى مالى": "costs_of_financial",
        "سود (زيان) عمليات در حال تداوم قبل از ماليات": "earings_before_taxes",
        "سود (زيان) خالص عمليات در حال تداوم": "earings_taxes",
        "سود (زيان) خالص": "net_profit",
        "جمع دارایی‌های غیرجاری": "fixed_assets",
        "موجودی مواد و کالا": "inventories",
        "جمع دارایی‌های جاری": "current_assets",
        "جمع دارایی‌ها": "total_assets",
        "جمع حقوق مالکانه": "stockholders_equity",
        "جمع بدهی‌های غیرجاری": "fixed_liabilities",
        "جمع بدهی‌های جاری": "current_liabilities",
        "جمع بدهی‌ها": "total_liabilities",
        "جریان ‌خالص ‌ورود‌ (خروج) ‌نقد حاصل از فعالیت‌های ‌عملیاتی": "net_cash_flow_from_operations",
        "جريان خالص ورود (خروج) نقد حاصل از فعاليت‌های سرمایه‌گذاری": "net_cash_flow_from_investing",
        "جريان خالص ورود (خروج) نقد حاصل از فعالیت‌های تامين مالی": "net_cash_flow_from_financing"
}




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

