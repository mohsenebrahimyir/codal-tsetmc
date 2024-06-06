import pandas as pd
from sqlalchemy import inspect

from codal_tsetmc.config.engine import engine


def fill_table_of_db_with_df(
    df: pd.DataFrame,
    table: str,
    columns: str = "",
    conditions: str = ""
):
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if table not in tables:
            from codal_tsetmc.models.create import create_table, models
            for model in models:
                if model.__tablename__ == table:
                    create_table(model)

        q = f"SELECT {columns} FROM {table} {conditions}"
        temp = pd.read_sql(q, engine)
        df = df[~df[columns].isin(temp[columns])]
    except Exception as e:
        print("fill_table_of_db_with_df: ", e.__context__, end="\r", flush=True)

    df.to_sql(table, engine, if_exists="append", index=False)


def read_table_by_conditions(table, variable="", value="", columns="*", conditions=""):
    query = f"SELECT {columns} FROM {table}"
    if conditions != "":
        query = f"{query} WHERE {conditions}"
    
    if variable != "" and value != "":
        query = f"{query} WHERE {variable} = '{value}'"

    return pd.read_sql(query, engine)


def read_table_by_sql_query(query: str):
    return pd.read_sql(query, engine)
