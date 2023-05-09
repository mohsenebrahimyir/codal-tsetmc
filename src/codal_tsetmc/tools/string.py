import re
from jdatetime import date as jd
from jdatetime import datetime as jdt

FA_TO_EN_DIGITS = {
    "۱": "1", "۲": "2", "۳": "3", "۴": "4", "۵": "5",
    "۶": "6", "۷": "7", "۸": "8", "۹": "9", "۰": "0",
}


AR_TO_FA_LETTER = {
    "ي": "ی",
    "ك": "ک"
}

EMPTY_TO_NONE = {
    "^$": None,
    "^--$": None
}

REMOVE_COMMA_AND_ADD_MINUS_SIGN = {
    "\,|\)": "",
    "\(": "-"
}

FIX_DIGITS = {**FA_TO_EN_DIGITS, **REMOVE_COMMA_AND_ADD_MINUS_SIGN}


SHEET_NAME_TO_ID = {
    "صورت وضعیت مالی": "0",
    "Balance Sheet": "0",
    "صورت سود و زیان": "1",
    "Income Statement": "1",
    "آمار تولید و فروش": "2",
    "Product Amount": "2",
    "صورت جریان های نقدی": "9",
    "Cash Flow": "9",
    "صورت سود و زیان تلفیقی": "13",
    "Consolidated Income Statement": "13",
    "صورت وضعیت مالی تلفیقی": "14",
    "Consolidated Balance Sheet": "14",
    "صورت جریان های نقدی تلفیقی": "15",
    "Consolidated Cash Flow": "15",
    "نظر حسابرس": "19",
    "Letter Auditing": "19",
    "خلاصه اطلاعات گزارش تفسیری - صفحه 1": "20",
    "Interpretative Report Summary - Page 1": "20",
    "خلاصه اطلاعات گزارش تفسیری - صفحه 2": "21",
    "Interpretative Report Summary - Page 2": "21",
    "خلاصه اطلاعات گزارش تفسیری - صفحه 3": "22",
    "Interpretative Report Summary - Page 3": "22",
    "خلاصه اطلاعات گزارش تفسیری - صفحه 4": "23",
    "Interpretative Report Summary - Page 4": "23",
    "خلاصه اطلاعات گزارش تفسیری - صفحه 5": "24",
    "Interpretative Report Summary - Page 5": "24",
    "صورت سود و زیان جامع": "1058",
    "Comprehensive Income Statement": "1058",
    "صورت تغییرات در حقوق مالکانه": "1060",
    "Changes In Property Rights": "1060",
    "صورت سود و زیان جامع تلفیقی": "1097",
    "Consolidated Comprehensive Income Statement": "1097",
    "صورت تغییرات در حقوق مالکانه تلفیقی": "1099",
    "Consolidated Changes In Property Rights": "1099",
    "توليد و فروش": "1197",
    "Production and sales": "1197",
}

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


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def datetime_to_num(dt):
    try:
        dt = replace_all(dt, {":": "", "/": "", "-": "", " ": ""})
        return int(dt) * 10 ** (14 - len(dt))
    except:
        return dt

def num_to_datetime(num, datetime = True, d = "/", t = ":", sep = " "):
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

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def value_to_float(x):
    x = x.replace(",", "")
    if type(x) == float or type(x) == int:
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


LETTERS_CODE_TO_TITLE = {
    "ن-10": "صورت های مالی میان دوره ای",
    "ن-11": "گزارش فعالیت هیئت مدیره",
    "ن-12": "گزارش کنترل داخلی",
    "ن-13": "زمان بندی پرداخت سود",
    "ن-20": "افشای اطلاعات با اهمیت",
    "ن-21": "شفاف سازی در خصوص شایعه، خبر یا گزارش منتشر شده",
    "ن-22": "شفاف سازی در خصوص نوسان قیمت سهام",
    "ن-23": "اطلاعات حاصل از برگزاری کنفرانس اطلاع رسانی",
    "ن-24": "درخواست ارایه مهلت جهت رعایت ماده ۱۹ مکرر ۱/ ۱۲ مکرر ۴ دستورالعمل اجرایی نحوه انجام معاملات",
    "ن-25": "برنامه ناشر جهت خروج از شمول ماده ۱۴۱ لایحه قانونی اصلاح قسمتی از قانون تجارت",
    "ن-26": "توضیحات در خصوص اطلاعات و صورت های مالی منتشر شده",
    "ن-30": "گزارش فعالیت ماهانه",
    "ن-41": "مشخصات کمیته حسابرسی و واحد حسابرسی داخلی",
    "ن-42": "آگهی ثبت تصمیمات مجمع عادی سالیانه",
    "ن-43": "اساسنامه شرکت مصوب مجمع عمومی فوق العاده",
    "ن-45": "معرفی/تغییر در ترکیب اعضای هیئت‌مدیره",
    "ن-50": "آگهی دعوت به مجمع عمومی عادی سالیانه",
    "ن-51": "خلاصه تصمیمات مجمع عمومی عادی سالیانه",
    "ن-52": "تصمیمات مجمع عمومی عادی سالیانه",
    "ن-53": "آگهی دعوت به مجمع عمومی عادی سالیانهنوبت دوم",
    "ن-54": "آگهی دعوت به مجمع عمومی عادی بطور فوق العاده",
    "ن-55": "تصمیمات مجمع عمومی عادی بطور فوق العاده",
    "ن-56": "آگهی دعوت به مجمع عمومی فوق العاده",
    "ن-57": "تصمیمات مجمع عمومی فوق‌العاده",
    "ن-58": "لغو آگهی (اطلاعیه) دعوت به مجمع عمومی",
    "ن-59": "مجوز بانک مرکزی جهت برگزرای مجمع عمومی عادی سالیانه",
    "ن-60": "پیشنهاد هیئت مدیره به مجمع عمومی فوق العاده در خصوص افزایش سرمایه",
    "ن-61": "اظهارنظر حسابرس و بازرس قانونی نسبت به گزارش توجیهی هیئت مدیره در خصوص افزایش سرمایه",
    "ن-62": "مدارک و مستندات درخواست افزایش سرمایه",
    "ن-63": "تمدید مهلت استفاده از مجوز افزایش سرمایه",
    "ن-64": "مهلت استفاده از حق تقدم خرید سهام",
    "ن-65": "اعلامیه پذیره نویسی عمومی",
    "ن-66": "نتایج حاصل از فروش حق تقدم های استفاده نشده",
    "ن-67": "آگهی ثبت افزایش سرمایه",
    "ن-69": "توزیع گواهی نامه نقل و انتقال و سپرده سهام",
    "ن-70": "تصمیم هیئت مدیره به انجام افزایش سرمایه تفویض شده در مجمع فوق العاده",
    "ن-71": "زمان تشکیل جلسه هیئت‌مدیره در خصوص افزایش سرمایه",
    "ن-72": "لغو اطلاعیه زمان تشکیل جلسه هیئت مدیره در خصوص افزایش سرمایه",
    "ن-73": "تصمیمات هیئت‌مدیره در خصوص افزایش سرمایه",
    "ن-80": "تغییر نشانی",
    "ن-81": "درخواست تکمیل مشخصات سهامداران",
}