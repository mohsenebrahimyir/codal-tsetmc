import re
import json
import requests
import pandas as pd
import jalali_pandas
from codal_tsetmc.tools.string_edit import *


def datetime_to_num(dt):
    try:
        dt = dt.replace(":", "").replace("/", "").replace(" ", "")
        return int(dt)
    except:
        return dt
    


def get_sheet_id(sheet: str):
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
    }

    if sheet in SHEET_NAME_TO_ID.keys():
        return f"&sheetId={SHEET_NAME_TO_ID[sheet]}"
    elif sheet in SHEET_NAME_TO_ID.values():
        return f"&sheetId={sheet}"
    else:
        return ""

def get_reports_from_codal(letter_serial: str, sheet: str = ""):
    sheet_id = get_sheet_id(sheet)
    url = f"https://codal.ir/Reports/Decision.aspx?LetterSerial={letter_serial}&rt=0&let=6&ct=0&ft=-1{sheet_id}"
    return requests.get(
        url=url, cookies={}, headers={
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
    )

def get_datasource(letter_serial: str, sheet: str = ""):
    letter = get_reports_from_codal(letter_serial, sheet)
    regex = r"var datasource = (.*);\r\n\r\n\r\n</script>"
    data_json = re.search(regex, letter.text)
    return json.loads(data_json.group(1))

def get_table_detail_v4(cells: dict):
    df = pd.DataFrame(cells)

    df["col"] = df["address"].str.slice(stop=1)
    df["row"] = df["address"].str.slice(start=1)

    item = df[df["col"] == "A"]
    head = df[df["row"] == "1"]

    item = dict(zip(item["row"], item["value"]))
    head = dict(zip(head["col"], head["value"]))

    df["item_fa"] = df["row"].replace(item)
    df["head"] = df["col"].replace(head)

    df = df[
        (df["col"] != "A") &
        (df["cellGroupName"] != "Header") &
        (df["item_fa"] != "1000") &
        (df["periodEndToDate"].dropna()) &
        (df["value"].dropna())
    ]

    df["value"] = pd.to_numeric(df["value"])
    df["item_en"] = df["item_fa"].replace(TRANSLATE_FA_TO_EN)
    df["periodEndToDate"] = df["periodEndToDate"].replace(regex={r"\/": ""}).apply(pd.to_numeric)
    df["yearEndToDate"] = df["yearEndToDate"].replace(regex={r"\/": ""}).apply(pd.to_numeric)
    df = df[["periodEndToDate", "yearEndToDate", "item_fa", "item_en", "value"]]

    return df


def get_balance_sheet(letter_serial: str):

    report = get_datasource(letter_serial, "Balance Sheet")

    for sheet in report["sheets"]:
        if sheet["title_En"] == "Balance Sheet":
            for table in sheet["tables"]:
                if table["title_En"] == "Balance Sheet":
                    cells = table["cells"]
                break

    if table["versionNo"] == "4":
        df = get_table_detail_v4(cells)
        df["version_no"] = table["versionNo"]
        df["alias_name"] = table["aliasName"]
        df["title_Fa"] = sheet["title_Fa"]
        df["title_En"] = sheet["title_En"]
        return df
    else:
        print("This version is not exist.")


def get_income_statement(letter_serial: str):

    report = get_datasource(letter_serial, "Income Statement")

    for sheet in report["sheets"]:
        if sheet["title_En"] == "Income Statement":
            for table in sheet["tables"]:
                if table["title_En"] == "Income Statement":
                    cells = table["cells"]
                break

    if table["versionNo"] == "6":
        df = get_table_detail_v4(cells)
        df["version_no"] = table["versionNo"]
        df["alias_name"] = table["aliasName"]
        df["title_Fa"] = sheet["title_Fa"]
        df["title_En"] = sheet["title_En"]
        return df
    else:
        print("This version is not exist.")


def get_cash_flow(letter_serial: str):

    report = get_datasource(letter_serial, "Cash Flow")

    for sheet in report["sheets"]:
        if sheet["title_En"] == "Cash Flow":
            for table in sheet["tables"]:
                if table["title_En"] == "Cash Flow":
                    cells = table["cells"]
                break

    if table["versionNo"] == "3":
        df = get_table_detail_v4(cells)
        df["version_no"] = table["versionNo"]
        df["alias_name"] = table["aliasName"]
        df["title_Fa"] = sheet["title_Fa"]
        df["title_En"] = sheet["title_En"]
        return df
    else:
        print("This version is not exist.")


def get_financial_statement_product_v4(letter_serial: str):

    report = get_datasource(letter_serial, "Balance Sheet")
    b_s = get_balance_sheet(letter_serial)
    i_s = get_income_statement(letter_serial)
    c_f = get_cash_flow(letter_serial)

    df = pd.concat([b_s, i_s, c_f])

    df["registerDateTime"] = datetime_to_num(report["registerDateTime"])
    df["period"] = int(report["period"])
    df["tracingNo"] = int(report["tracingNo"])
    df["isConsolidated"] = bool(report["isConsolidated"])
    df["isAudited"] = bool(report["isAudited"])

    return df_col_to_snake_case(df)
