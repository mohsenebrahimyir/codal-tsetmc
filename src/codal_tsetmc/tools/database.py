import pandas as pd
from codal_tsetmc.tools.string import AR_TO_FA_LETTER
from sqlalchemy import inspect

from codal_tsetmc.config.engine import engine, Base


def fill_table_of_db_with_df(
        df: pd.DataFrame,
        table: str,
        columns: str = "",
        conditions: str = ""
):
    try:
        q = f"SELECT {columns} FROM {table} {conditions}"
        temp = pd.read_sql(q, engine)
        df = df[~df[columns].isin(temp[columns])].replace(regex=AR_TO_FA_LETTER)
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


def is_table_exist_in_db(table: str) -> bool:
    return table in get_tables_name_in_db()


def create_table_if_not_exist(model: Base):
    if not is_table_exist_in_db(model.__tablename__):
        model.__table__.create(engine)


def get_tables_name_in_db() -> list:
    inspector = inspect(engine)
    return inspector.get_table_names()


def delete_table_in_db(table: str) -> bool:
    try:
        q = f"DROP TABLE {table}"
        read_table_by_sql_query(q)
        print(f"Table {table} deleted.")
        return True
    except Exception as e:
        print(e.__context__)
        return False


def delete_all_tables_in_db() -> bool:
    try:
        for table in get_tables_name_in_db():
            delete_table_in_db(table)
        return True
    except Exception as e:
        print(e.__context__)
        return False
