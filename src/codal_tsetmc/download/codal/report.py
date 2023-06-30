import re
import json
import requests
import pandas as pd
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import jalali_pandas
from codal_tsetmc.tools import *
from codal_tsetmc import db

def get_sheet_id(sheet: str) -> str:
    if sheet in SHEET_NAME_TO_ID.keys():
        return f"&sheetId={SHEET_NAME_TO_ID[sheet]}"
    elif sheet in SHEET_NAME_TO_ID.values():
        return f"&sheetId={sheet}"
    else:
        return ""

def get_letter(letter_serial: str, sheet: str = "") -> str:
    sheet_id = get_sheet_id(sheet)
    headers={
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    url = f"https://codal.ir/Reports/Decision.aspx?LetterSerial={letter_serial}&rt=0&let=6&ct=0&ft=-1{sheet_id}"
    response = requests.get(url=url, cookies={}, headers=headers)
    return response.text

async def get_letter_async(serial: str, sheet: str = ""):
    id = get_sheet_id(sheet)
    url = f"https://codal.ir/Reports/Decision.aspx?LetterSerial={serial}&rt=0&let=6&ct=0&ft=-1{id}"
    headers={
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, cookies={}) as resp:
            response = await resp.text()
            return response

def get_options(letter_string: str):
    soup = BeautifulSoup(letter_string, 'html.parser')
    return {item.get("value"): item.string for item in soup.find_all("option")}

def get_symbol_and_name(letter_string: str) -> str:
    soup = BeautifulSoup(letter_string, 'html.parser')
    return {
        "name": soup.find(id="ctl00_txbCompanyName").string,
        "capital": int(soup.find(id="ctl00_lblListedCapital").string.replace(",", "")),
        "symbol": soup.find(id="ctl00_txbSymbol").string,
        "isic": soup.find(id="ctl00_lblISIC").string,
        "state": soup.find(id="ctl00_lblCompanyState").string,
    } 


def get_datasource(letter_string: str) -> dict:
    regex = r"datasource = (.*);\r\n\r\n\r\n</script>"
    data_json = re.search(regex, letter_string)
    return json.loads(data_json.group(1))


def get_datasource_detail(datasource: dict) -> dict:
    return {
        "title_fa": datasource['title_Fa'],
        "title_en": datasource['title_En'],
        "period_end_to_date": datetime_to_num(datasource["periodEndToDate"]),
        "year_end_to_date": datetime_to_num(datasource["yearEndToDate"]),
        "register_date_time": datetime_to_num(datasource["registerDateTime"]),
        "sent_date_time": datetime_to_num(datasource["sentDateTime"]),
        "publish_date_time": datetime_to_num(datasource["publishDateTime"]),
        "period_extra_day": datetime_to_num(datasource['periodExtraDay']),
        "is_consolidated": datasource['isConsolidated'],
        "tracing_no": datasource['tracingNo'],
        "is_audited": datasource['isAudited'],
        "audit_state": datasource['auditState'],
        "state": datasource['state'],
        "is_for_auditing": datasource['isForAuditing'],
        "period": datasource['period'],
    }

def get_sheet(datasource, sheet: str = "صورت سود و زیان") -> dict:
    for sht in datasource["sheets"]:
        if sht["title_Fa"] == sheet:
            return sht

def get_sheet_detail(sheet: dict) -> dict:
    return {
        "sheet_title_fa": sheet['title_Fa'],
        "sheet_title_en": sheet['title_En'],
    }

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

def get_table(sheet: dict, table: str = "صورت سود و زیان") -> pd.DataFrame:
    for tbl in sheet["tables"]:
        if tbl["title_Fa"] == table:
            return tbl

def get_table_detail(table: dict) -> dict:
    return {
        "table_title_en": None if table["title_En"] is None else table["title_En"].replace("Statment", "Statement"),
        "table_title_fa": table["title_Fa"],
        "table_description": table['description'],
        "table_alias_name": table['aliasName']
    }

def get_cells(table: dict) -> pd.DataFrame:
    df = pd.DataFrame(table["cells"])
    df["value"] = df["value"].replace(regex=AR_TO_FA_LETTER).replace(regex=EMPTY_TO_NONE)
    df["row"] = df["address"].str.slice(start=1)
    df["col"] = df["address"].str.slice(stop=1)
    df = df[(df['value'].notna()) & (df["isVisible"]) & (df["cellGroupName"] == "Body")]

    return df

def get_items(df: pd.DataFrame) -> pd.DataFrame:
    item = df[
        df.valueTypeName.isin(["Fix", "Component"])
    ].rename(columns={"value": "item"})[
        ["row", "category", "item"]
    ]

    return item

def get_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df[(
        (df.valueTypeName == "FormControl") | 
        (df.valueTypeName == "-1")
    )]
    df = df[(df.periodEndToDate != "")]
    df["period_end_to_date"] = df["periodEndToDate"].apply(datetime_to_num)
    df["year_end_to_date"] = df["yearEndToDate"].apply(datetime_to_num)
    
    df["value"] = pd.to_numeric(df["value"])
    df["cell_id"] = (
        df["metaTableId"].astype(str) + 
        '-' + df["metaTableCode"].astype(str) +
        '-' + df["address"].astype(str) +
        '-' + df["category"].astype(str) +
        '-' + df["period_end_to_date"].astype(str)
    )
    
    df = df[[
        "row", "category", "cell_id",
        "period_end_to_date",
        "year_end_to_date",
        "value"
    ]]
    return  df

def get_table_of_item_and_value_df(table_dict: dict) -> pd.DataFrame:
    cells_df = get_cells(table_dict)
    items_df = get_items(cells_df)
    values_df = get_values(cells_df)
    df = pd.merge(values_df, items_df)[[
        "cell_id", "period_end_to_date", "year_end_to_date", "item", "value"
    ]]

    return df

def update_head_of_financial_statment(letter_string: str):

    symbol_and_name_dict = get_symbol_and_name(letter_string)
    datasource_dict = get_datasource(letter_string)
    datasource_detail_dict = get_datasource_detail(datasource_dict)

    df = pd.DataFrame.from_records(
        [{**symbol_and_name_dict, **datasource_detail_dict}]
    )

    fill_table_of_db_with_df(df, "financial_statement", "tracing_no")


def update_balance_sheet_income_statement_cash_flow_table(df):
    fill_table_of_db_with_df(df, "balance_sheet_income_statement_cash_flow", "cell_id")
    
