import re
import json
import requests
import pandas as pd
import sys
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from codal_tsetmc.tools.api import get_results_by_asyncio_loop
from codal_tsetmc.tools.string import (
    SHEET_NAME_TO_ID, EMPTY_TO_NONE, AR_TO_FA_LETTER,
    to_snake_case,
    df_col_to_snake_case,
    datetime_to_num,
    replace_all,
)
from codal_tsetmc.tools.database import fill_table_of_db_with_df
from codal_tsetmc.models.companies import Letters

def extract_sheet_id(sheet: str) -> str:
    if sheet in SHEET_NAME_TO_ID.keys():
        return f"&sheetId={SHEET_NAME_TO_ID[sheet]}"
    elif sheet in SHEET_NAME_TO_ID.values():
        return f"&sheetId={sheet}"
    else:
        return ""

def get_letter(letter_serial: str, sheet: str = "") -> str:
    sheet_id = extract_sheet_id(sheet)
    headers={
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    url = f"https://codal.ir/Reports/Decision.aspx?LetterSerial={letter_serial}&rt=0&let=6&ct=0&ft=-1{sheet_id}"
    response = requests.get(url=url, cookies={}, headers=headers)
    return response.text

async def get_letter_async(serial: str, sheet: str = ""):
    id = extract_sheet_id(sheet)
    url = f"https://codal.ir/Reports/Decision.aspx?LetterSerial={serial}&rt=0&let=6&ct=0&ft=-1{id}"
    headers={
        "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, cookies={}) as resp:
            response = await resp.text()
            return response

def extract_options(letter_string: str):
    soup = BeautifulSoup(letter_string, 'html.parser')
    return [item.get("value") for item in soup.find_all("option")]

def extract_symbol_and_name(letter_string: str) -> str:
    soup = BeautifulSoup(letter_string, 'html.parser')
    return {
        "name": soup.find(id="ctl00_txbCompanyName").string,
        "capital": int(soup.find(id="ctl00_lblListedCapital").string.replace(",", "")),
        "symbol": soup.find(id="ctl00_txbSymbol").string,
        "isic": soup.find(id="ctl00_lblISIC").string,
        "company_state": soup.find(id="ctl00_lblCompanyState").string,
    } 


def edit_datasource_detail(datasource: dict) -> dict:
    datasource = {to_snake_case(k):v for k,v in datasource.items()}
    dates = [
        "period_end_to_date", 
        "year_end_to_date",
        "register_date_time",
        "sent_date_time",
        "publish_date_time"
    ]
    for date in dates:
        datasource[date] = datetime_to_num(datasource[date])

    return datasource

def extract_datasource(letter_string: str) -> dict:
    regex = r"datasource = (.*);\r\n"
    data_json = re.search(regex, letter_string)
    datasource = json.loads(data_json.group(1))
    return edit_datasource_detail(datasource)


def update_financial_statment_header(letter_string: str):

    symbol_and_name = extract_symbol_and_name(letter_string)
    datasource = extract_datasource(letter_string)

    df = pd.DataFrame.from_records(
        [{**symbol_and_name, **datasource}]
    )

    df = df[[
        "name", 
        "capital",
        "symbol",
        "isic",
        "company_state",
        "title_fa",
        "title_en",
        "period_end_to_date",
        "year_end_to_date",
        "register_date_time",
        "sent_date_time",
        "publish_date_time",
        "period_extra_day",
        "is_consolidated",
        "tracing_no",
        "is_audited",
        "audit_state",
        "is_for_auditing",
        "period",
        "state"
    ]]

    fill_table_of_db_with_df(df, "financial_statement_header", "tracing_no")

def edit_sheet_detail(sheet: dict) -> dict:
    return {to_snake_case(k):v for k,v in sheet.items()}

def extract_sheet(datasource, sheet: str = "صورت سود و زیان") -> dict:
    for sht in datasource["sheets"]:
        if sht["title_Fa"] == sheet:
            return edit_sheet_detail(sht)

def extract_sheet_components(sheet: dict) -> dict:
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

def edit_table_detail(table: dict) -> dict:
    if table["title_En"] is not None:
        table["title_En"] = replace_all(table["title_En"], {
            "BalanceSheet": "Balance Sheet",
            "Income Statment": "Income Statement"
        })
    else:
        table["title_En"] = None
    
    return {to_snake_case(k):v for k,v in table.items()}

def extract_table(sheet: dict, table: str = "صورت سود و زیان") -> pd.DataFrame:
    for tbl in sheet["tables"]:
        if tbl["title_Fa"] == table:
            return edit_table_detail(tbl)

def extract_cells(table: dict) -> pd.DataFrame:
    df = pd.DataFrame(table["cells"])
    df = df_col_to_snake_case(df)
    df = df.replace(regex=AR_TO_FA_LETTER).replace(regex=EMPTY_TO_NONE)
    df["row"] = df["address"].str.slice(start=1)
    df["col"] = df["address"].str.slice(stop=1)
    df = df[
        (df['value'].notna()) & 
        (df["is_visible"]) &
        (df["cell_group_name"] == "Body")
    ]

    return df.drop_duplicates()

def extract_items(df: pd.DataFrame) -> pd.DataFrame:
    if "value_type_name" in df.columns:
        df = df[df["value_type_name"].isin(["Fix", "Component"])]
    else:
        df = df[df["col"].isin(["A"])]

    df = df.rename(columns={"value": "item"})[["row", "category", "item"]]

    return df.drop_duplicates()

def extract_values(df: pd.DataFrame) -> pd.DataFrame:
    if "value_type_name" in df.columns:
        df = df[df["value_type_name"].isin(["FormControl", "-1"])]
    else:
        df = df[df["data_type_name"].isin(["Currency"])]
    
    df = df[~pd.isna(df["period_end_to_date"])]
    
    df["period_end_to_date"] = df["period_end_to_date"].apply(datetime_to_num)

    if "year_end_to_date" in df.columns:
        df["year_end_to_date"] = df["year_end_to_date"].apply(datetime_to_num)
        df[["period_end_to_date", "year_end_to_date"]] = df[
            ["period_end_to_date", "year_end_to_date"]
        ].fillna(method="ffill", axis=1, limit=1)
    else:
        df["year_end_to_date"] = df["period_end_to_date"]
    
    df["value"] = pd.to_numeric(df["value"])
    df["cell_id"] = (
        df["meta_table_id"].astype(str) + 
        '-' + df["meta_table_code"].astype(str) +
        '-' + df["address"].astype(str) +
        '-' + df["category"].astype(str) +
        '-' + df["period_end_to_date"].astype(str)
    )
    
    df = df[[
        "row", "value", "cell_id", "category",
        "year_end_to_date", "period_end_to_date",
    ]]
    return  df.drop_duplicates()




def extract_table_with_single_item(table: dict) -> pd.DataFrame:
    cells = extract_cells(table)
    items = extract_items(cells)
    values = extract_values(cells)
    df = pd.merge(values, items)[[
        "cell_id", "period_end_to_date", 
        "year_end_to_date", "item", "value"
    ]]

    return df.drop_duplicates()


def add_sheet_and_table_detail(df, datasource, sheet, table):
    df["tracing_no"] = datasource["tracing_no"]
    df["cell_id"] = df["tracing_no"].astype(str) + '-' + df["cell_id"]
    df["sheet_title_en"] = sheet["title_en"]
    df["sheet_title_fa"] = sheet["title_fa"]
    df["table_title_en"] = table["title_en"]
    df["table_title_fa"] = table["title_fa"]
    df["description"] = table["description"]
    df["alias_name"] = table["alias_name"]
    return df


TABLES_WHIT_SINGLE_ITEM = [
    "Balance Sheet", 
    "Income Statement",
    "Cash Flow",
    "Sales trend and cost over the last 5 years",
    "The cost of the sold goods", 
    "Staff status",
    "Other operating income",
    "Other operating expenses",
    "Non-operation income and expenses investment income",
    "Non-operation income and expenses miscellaneous items"
]

def update_financial_statement_table(datasource, sheet, table):
    sheet = edit_sheet_detail(sheet)
    table = edit_table_detail(table)
    if table["title_en"] in TABLES_WHIT_SINGLE_ITEM:
        df = extract_table_with_single_item(table)
        db_table = "financial_statement_table_with_single_item"
        df = add_sheet_and_table_detail(df, datasource, sheet, table)
        fill_table_of_db_with_df(df, db_table, "cell_id")
    

async def update_stock_financial_statement_table_async(symbol, from_date = 1400, to_date = 1500):

    letter_serials = Letters.query.filter(
        Letters.symbol == symbol,
        Letters.publish_date_time > datetime_to_num(from_date),
        Letters.publish_date_time < datetime_to_num(to_date),
        Letters.letter_types == "صورت های مالی میان دوره ای"
    )

    serials = [serial.letter_serial for serial in letter_serials]

    for i, serial in enumerate(serials):
        print(i, serial)
        options = ["0"]
        option_active = True
        while option_active:
            option = options[0]
            letter_string = await get_letter_async(serial, option)
            if option == "0":
                options = extract_options(letter_string)
                if "19" in options: options.remove("19")
            
            if "datasource" in letter_string:
                update_financial_statment_header(letter_string)

                datasource = extract_datasource(letter_string)
                for sheet in datasource["sheets"]:
                    for table in sheet["tables"]:
                        if table["cells"] != []:
                            update_financial_statement_table(datasource, sheet, table)
                
            options.remove(option)
            if options == []: option_active = False



def update_stocks_financial_statement_table(symbols, from_date = 1400, to_date = 1500, msg=""):
    if symbols.__class__ != list:
        symbols = [symbols]
    
    tasks = [update_stock_financial_statement_table_async(symbol, from_date, to_date) for symbol in symbols]
    get_results_by_asyncio_loop(tasks)
    print(msg, end="\r")
