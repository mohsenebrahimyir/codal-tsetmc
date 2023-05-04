import pandas as pd

import codal_tsetmc.config as db


def fill_table_of_db_with_df(
    data: pd.DataFrame,
    table: str,
    columns: str = "date",
    conditions: str = "",
    text: str = ""
):
    try:
        q = f"select {columns} from {table} {conditions}"
        temp = pd.read_sql(q, db.engine)
        data = data[~data[columns].isin(temp[columns])]
    except:
        pass

    data.to_sql(
        table, db.engine,
        if_exists="append",
        index=False
    )
    print(text, end="\r", flush=True)
