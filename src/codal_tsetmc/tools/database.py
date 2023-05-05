import pandas as pd

import codal_tsetmc.config as db


def fill_table_of_db_with_df(
    df: pd.DataFrame,
    table: str,
    columns: str = "",
    conditions: str = "",
    text: str = ""
):
    try:
        q = f"select {columns} from {table} {conditions}"
        temp = pd.read_sql(q, db.engine)
        df = df[~df[columns].isin(temp[columns])]
    except:
        pass

    df.to_sql(table, db.engine, if_exists="append", index=False)
    print(text, end="\r", flush=True)

