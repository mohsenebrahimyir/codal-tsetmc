import pandas as pd
from sqlalchemy import inspect

from codal_tsetmc.config.engine import engine


def is_table_exist_in_db(table: str) -> bool:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return table in tables


def fill_table_of_db_with_df(
        df: pd.DataFrame,
        table: str,
        columns: str = "",
        conditions: str = ""
):
    try:
        q = f"SELECT {columns} FROM {table} {conditions}"
        temp = pd.read_sql(q, engine)
        df = df[~df[columns].isin(temp[columns])]
        df.to_sql(table, engine, if_exists="append", index=False)

        print(f"Table {table} updated.")
        return True

    except Exception as e:
        print(f"Missing in {table} table with conditions: {conditions}", e.__context__)
        return False


def read_table_by_conditions(table, variable="", value="", columns="*", conditions=""):
    query = f"SELECT {columns} FROM {table}"
    if conditions != "":
        query = f"{query} WHERE {conditions}"
    
    if variable != "" and value != "":
        query = f"{query} WHERE {variable} = '{value}'"

    return pd.read_sql(query, engine)


def read_table_by_sql_query(query: str):
    return pd.read_sql(query, engine)
