import pandas as pd

from codal_tsetmc.config.engine import engine


def fill_table_of_db_with_df(
    df: pd.DataFrame,
    table: str,
    columns: str = "",
    conditions: str = "",
    text: str = ""
):
    try:
        q = f"SELECT {columns} FROM {table} {conditions}"
        temp = pd.read_sql(q, engine)
        df = df[~df[columns].isin(temp[columns])]
    except:
        pass

    df.to_sql(table, engine, if_exists="append", index=False)
    print(text, end="\r", flush=True)


def read_table_by_conditions(table, variable="", value="", columns="*", conditions=""):
    query = f"SELECT {columns} FROM {table}"
    if conditions != "":
        query = f"{query} WHERE {conditions}"
    
    if variable != "" and value != "":
        query = f"{query} WHERE {variable} = '{value}'"

    return pd.read_sql(query, engine)
