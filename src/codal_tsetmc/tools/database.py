import pandas as pd
from sqlalchemy import Engine, inspect, text, bindparam

from ..config.engine import engine as db, Base
from ..tools.string import REPLACE_INCORRECT_CHARS
from pandas.api.types import is_string_dtype


def fill_table_of_db_with_df(
    df: pd.DataFrame,
    table: str,
    unique: str | None = None,
    engine: Engine = db,
): 
    try:
        if df.empty:
            return True

        if unique:
            df = df.drop_duplicates(subset=unique).reset_index(drop=True).copy()
            if is_string_dtype(df[unique]):
                conditions = ",".join([f"'{str(x)}'" for x in df[unique]])
                df[unique] = df[unique].replace(regex=REPLACE_INCORRECT_CHARS)
            else:
                conditions = ",".join([f"{str(x)}" for x in df[unique]])

            with engine.connect() as conn:
                q = f"SELECT {unique} FROM {table} WHERE {unique} IN ({conditions});"
                result = conn.execute(text(q))
                exist_records = result.all()

            if exist_records:
                existing_values = [x[0] for x in exist_records]
                df = df[~df[unique].isin(existing_values)].copy()

            if df.empty:
                return True

        try:
            str_cols = df.select_dtypes(include=["object", "string"]).columns
            for col in str_cols:
                df[col] = df[col].replace(regex=REPLACE_INCORRECT_CHARS)
        except Exception as e:
            print(f"Data cleaning warning: {e}")

        df.to_sql(table, engine, if_exists="append", index=False)
        print(f"Successfully updated table {table} with {len(df)} records.")
        return True

    except Exception as e:
        print(f"Error in fill_table_of_db_with_df: {str(e)}")
        return False


def read_table_by_conditions(
    table,
    variable="",
    value="",
    columns="*",
    conditions="",
    engine: Engine = db,
):
    try:
        query = f"SELECT {columns} FROM {table}"
        if conditions != "":
            query = f"{query} WHERE {conditions}"

        if variable != "" and value != "":
            query = f"{query} WHERE {variable} = '{value}'"

        with engine.connect() as conn:
            result = conn.execute(text(query))
            exist_records = result.all()

        if exist_records:
            return pd.DataFrame(exist_records)
        else:
            return pd.DataFrame()

    except Exception as e:
        print(f"Error in read_table_by_conditions: {str(e)}")
        return pd.DataFrame()


def read_table_by_sql_query(
    query: str,
    engine: Engine = db,
):
    with engine.connect() as conn:
        result = conn.execute(text(query))
        exist_records = result.all()

    if exist_records:
        return pd.DataFrame(exist_records)
    else:
        return pd.DataFrame()


def is_table_exist_in_db(table: str) -> bool:
    return table in get_tables_name_in_db()


def create_table_if_not_exist(
    model: Base,
    engine: Engine = db,
):
    if not is_table_exist_in_db(model.__tablename__):
        model.__table__.create(engine)


def get_tables_name_in_db(engine: Engine = db) -> list:
    inspector = inspect(engine)
    return inspector.get_table_names()


def delete_table_in_db(
    table: str,
    engine: Engine = db,
) -> bool:
    try:
        q = f"DROP TABLE {table}"
        read_table_by_sql_query(q, engine)
        print(f"Table {table} deleted.")
        return True
    except Exception as e:
        print(e.__context__)
        return False


def delete_all_tables_in_db(engine: Engine = db) -> bool:
    try:
        for table in get_tables_name_in_db():
            delete_table_in_db(table, engine)
        return True
    except Exception as e:
        print(f"Error in delete_all_tables_in_db: {str(e)}")
        return False
