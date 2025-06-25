import pandas as pd
from codal_tsetmc.tools.string import AR_TO_FA_LETTER
from sqlalchemy import inspect, text

from codal_tsetmc.config.engine import engine, Base


def fill_table_of_db_with_df(
        df: pd.DataFrame,
        table: str,
        columns: str = "",
        conditions: str = ""
):
    try:
        # print("df:", df)
        # print("table:", table)
        # print("columns:", columns)
        # print("conditions:", conditions)

        if not conditions:
            conditions = (
                f"""WHERE {columns} IN ('{"','".join(df[columns].to_list())}');"""
            )

        q = f"SELECT {columns} FROM {table} {conditions}"
        # print("q:", q)

        with engine.connect() as conn:
            result = conn.execute(text(q))
            exist_records = result.all()

        # print("exist_records:", exist_records)

        if exist_records:
            temp = pd.DataFrame(exist_records)
            # print("temp:", temp)
            df = df[~df[columns].isin(temp[columns].to_list())]
            # print("df:", df)
        
        try:
            df.replace(regex=AR_TO_FA_LETTER, inplace=True)
        except Exception as e:
            print("")
            pass
        
        df.to_sql(table, engine, if_exists="append", index=False)
        print(f"Table {table} updated.")
        return True

    except Exception as e:
        print(f"Missing in fill_table_of_db_with_df:", e)
        return False


def read_table_by_conditions(table, variable="", value="", columns="*", conditions=""):
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
        print(f"Missing in read_table_by_conditions:", e.__context__)
        return False


def read_table_by_sql_query(query: str):
    with engine.connect() as conn:
        result = conn.execute(text(query))
        exist_records = result.all()

    if exist_records:
        return pd.DataFrame(exist_records)
    else:
        return pd.DataFrame()


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
