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


def datetime_to_num(dt):
    if dt == "":
        print("datetime_to_num is None", end="\r", flush=True)
        return None
    try:
        dt = replace_all(dt, {"[^0-9]": ""})
        return int(dt) * 10 ** (14 - len(dt))
    except Exception as e:
        print("datetime_to_num: ", e.__context__, end="\r", flush=True)
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
