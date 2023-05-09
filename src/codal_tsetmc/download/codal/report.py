import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
import jalali_pandas
from codal_tsetmc.tools.string import *

def get_sheet_id(sheet: str) -> str:

    if sheet in SHEET_NAME_TO_ID.keys():
        return f"&sheetId={SHEET_NAME_TO_ID[sheet]}"
    elif sheet in SHEET_NAME_TO_ID.values():
        return f"&sheetId={sheet}"
    else:
        return ""

def get_letter(letter_serial: str, sheet: str = "") -> str:
    sheet_id = get_sheet_id(sheet)
    url = f"https://codal.ir/Reports/Decision.aspx?LetterSerial={letter_serial}&rt=0&let=6&ct=0&ft=-1{sheet_id}"
    return requests.get(
        url=url, cookies={}, headers={
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
    )

def get_symbol_and_name(letter: str) -> str:
    soup = BeautifulSoup(letter.text, 'html.parser')
    return {
        "CompanyName": replace_all(soup.find(id="ctl00_txbCompanyName").string, AR_TO_FA_LETTER),
        "ListedCapital": int(soup.find(id="ctl00_lblListedCapital").string.replace(",", "")),
        "Symbol": replace_all(soup.find(id="ctl00_txbSymbol").string, AR_TO_FA_LETTER),
        "UnauthorizedCapital": soup.find(id="ctl00_divUnauthorizedCapital").string,
        "ISIC": int(soup.find(id="ctl00_lblISIC").string),
        "Period": int(soup.find(id="ctl00_lblPeriod").string.replace(" ماهه", "")),
        "PeriodEndToDate": datetime_to_num(soup.find(id="ctl00_lblPeriodEndToDate").string),
        "IsAudited": replace_all(soup.find(id="ctl00_lblIsAudited").string, AR_TO_FA_LETTER),
        "YearEndToDate": datetime_to_num(soup.find(id="ctl00_lblYearEndToDate").string),
        "CompanyState": replace_all(soup.find(id="ctl00_lblCompanyState").string, AR_TO_FA_LETTER),
    } 


def get_datasource(letter: str) -> dict:
    regex = r"var datasource = (.*);\r\n\r\n\r\n</script>"
    data_json = re.search(regex, letter.text)
    return json.loads(data_json.group(1))


def get_datasource_detail(datasource: dict) -> dict:
    detail = removekey(datasource, "sheets")
    detail['datasource_title_en'] = detail['title_En'].replace(" ", "")
    detail["periodEndToDate"] = datetime_to_num(detail["periodEndToDate"])
    detail["yearEndToDate"] = datetime_to_num(detail["yearEndToDate"])
    detail["registerDateTime"] = datetime_to_num(detail["registerDateTime"])
    detail["sentDateTime"] = datetime_to_num(detail["sentDateTime"])
    detail["publishDateTime"] = datetime_to_num(detail["publishDateTime"])
    return detail

def get_sheet(datasource, sheet: str = "Income Statement") -> dict:
    for sht in datasource["sheets"]:
        if sht["title_En"] == sheet:
            return sht

def get_sheet_datail(sheet: dict) -> dict:
    detail = removekey(sheet, "tables")
    detail = removekey(detail, "sheetComponents")
    return detail

def get_sheet_components(sheet: dict) -> dict:
    products = pd.DataFrame({"text": [], "value": []})
    # units = pd.DataFrame({"text": [],  "value": []})
    for id in sheet["sheetComponents"].keys():
        detail = sheet["sheetComponents"][id][0]
        if detail["typeName"] != "Date":
            if detail["data"][0]["params"] == []:
                df = pd.DataFrame(detail["data"])
                products = pd.concat([products, df[["text", "value"]]])
            else:
                #TODO: add units of products
                pass

    return products

def get_table(sheet: dict, table: str = "Income Statement") -> pd.DataFrame:
    for tbl in sheet["tables"]:
        if tbl["title_En"] == table:
            return tbl

def get_table_datail(table: dict) -> dict:
    detail = removekey(table, "cells")
    return detail

def get_cells(table: dict) -> pd.DataFrame:
    df = pd.DataFrame(table["cells"])
    df["value"] = df["value"].replace(regex=AR_TO_FA_LETTER).replace(regex=EMPTY_TO_NONE)
    df["row"] = df["address"].str.slice(start=1)
    df["col"] = df["address"].str.slice(stop=1)
    return df[(df['value'].notna()) & (df["isVisible"]) & (df["cellGroupName"] == "Body")]

def get_items(df: pd.DataFrame) -> pd.DataFrame:
    item = df[
        df.valueTypeName.isin(["Fix", "Component"])
    ].rename(columns={"value": "item"})
    return item[["row", "category", "item"]]

def filter_amount_of_money(df: pd.DataFrame) -> pd.DataFrame:
    cols = df[df.value == "مبلغ فروش (میلیون ریال)"].col.unique()
    df = df[df.col.isin(cols)]
    df = df[df.cellGroupName == "Body"]
    return df

def get_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        ((df.valueTypeName == "FormControl") | (df.valueTypeName == "-1"))
    ][["row", "category", "periodEndToDate", "yearEndToDate", "value"]]
    df["value"] = pd.to_numeric(df["value"])
    return  df

def get_financial_statement_product(letter_serial: str, sheet: str = "", table: str = "") -> pd.DataFrame:
    letter_str = get_letter(letter_serial, sheet)
    datasource_dict = get_datasource(letter_str)
    datasource_detail_dict = get_datasource_detail(datasource_dict)
    sheet_dict = get_sheet(datasource_dict, sheet)
    table_dict = get_table(sheet_dict, table)
    table_datail_dict = get_table_datail(table_dict)
    cells_df = get_cells(table_dict)
    items_df = get_items(cells_df)
    values_df = get_values(cells_df)

    df = pd.merge(items_df, values_df, on=["row", "category"])

    for col in ["periodEndToDate", "yearEndToDate", "item"]:
        df[col] = df[col].replace(regex=AR_TO_FA_LETTER).replace(regex=EMPTY_TO_NONE)
        df = df[df[col] != "1000"]
        if col != "item":
            df[col] = df[col].replace(regex={r"\/": ""}).apply(pd.to_numeric) * 1000000
    
    df = df[["periodEndToDate", "yearEndToDate", "item", "value"]].reset_index(drop="index")

    df["datasource_title_en"] = datasource_detail_dict["datasource_title_en"]
    df["registerDateTime"] = datasource_detail_dict["registerDateTime"]
    df["sentDateTime"] = datasource_detail_dict["sentDateTime"]
    df["publishDateTime"] = datasource_detail_dict["publishDateTime"]
    df["tracingNo"] = datasource_detail_dict["tracingNo"]
    df["period"] = datasource_detail_dict["period"]
    df["isAudited"] = datasource_detail_dict["isAudited"]
    df["sheet_title_En"] = table_datail_dict["aliasName"]
    df["sheet_title_Fa"] = table_datail_dict["title_Fa"]

    return df_col_to_snake_case(df)
