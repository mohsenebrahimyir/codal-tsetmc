import re
import json
import requests
import bs4
import pandas as pd
from codal_tsetmc.tools.string_edit import *


def get_datasource(letter_serial: str, item: str = ""):
    url = f"https://codal.ir/Reports/Decision.aspx?LetterSerial={letter_serial}&rt=0&let=6&ct=0&ft=-1{item}"
    response = requests.get(
        url=url, cookies={}, headers={
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
    )
    regex = r"var datasource = (.*);\r\n\r\n\r\n</script>"
    data_json = re.search(regex, response.text)
    return json.loads(data_json.group(1))

def get_financial_statement(letter_serial: str, item: str = ""):
    if item == "BalanceSheet" or item == "0":
        item = "&sheetId=0"
    elif item == "IncomeStatement" or item == "1":
        item = "&sheetId=1"
    elif item == "CashFlow" or item == "9":
        item = "&sheetId=9"

    report = get_datasource(letter_serial, item)
    df = pd.DataFrame(report["sheets"][0]["tables"][0]["cells"])

    df["col"] = df.address.str.slice(stop=1)
    df["row"] = df.address.str.slice(start=1)

    item = df[df.col == "A"]
    item = dict(zip(item.row, item.value))
    df["item"] = df["row"].replace(item)

    head = df[df.row == "1"]
    head = dict(zip(head.col, head.value))
    df["head"] = df["col"].replace(head)

    df = df[
        (df.col != "A") &
        (df.cellGroupName != "Header") &
        (df.item != "1000") &
        (df["periodEndToDate"].dropna()) &
        (df["value"].dropna()) &
        (df.periodEndToDate == report["periodEndToDate"])
    ]
    
    df = df[["periodEndToDate", "item", "value"]]
    df["value"] = pd.to_numeric(df.value)
    df["item"] = df.item.replace(TRANSLATE_FA_TO_EN)
    df = df[df.item.isin(TRANSLATE_FA_TO_EN.values())]
    df["registerDateTime"] = report["registerDateTime"]
    df["aliasName"] =  report["sheets"][0]["tables"][0]["aliasName"]
    df["period"] = pd.to_numeric(report["period"])
    df["tracingNo"] = pd.to_numeric(report["tracingNo"])
    df["publishDateTime"] = report["publishDateTime"]
    df["yearEndToDate"] = report["yearEndToDate"]
    df["isAudited"] = report["isAudited"]

    return df

def get_financial_statements(letter_serial: str):
    df0 = get_financial_statement(letter_serial, "0")
    df1 = get_financial_statement(letter_serial, "1")
    df9 = get_financial_statement(letter_serial, "9")
    df = pd.concat([df0, df1, df9], ignore_index=True)
    df = df.pivot(
        index=[
            "periodEndToDate", "yearEndToDate", "registerDateTime", 
            "publishDateTime", "tracingNo", "isAudited", "period", 
        ], columns="item", values="value"
    )
    df.columns.name = None
    df = df.reset_index()
    return df
     