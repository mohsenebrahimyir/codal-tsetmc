import os

import codal_tsetmc.config as db
from .download import *
from codal_tsetmc.models import *
from codal_tsetmc.tools import *

from .initializer import init_db, fill_db


def db_is_empty():
    try:
        db.session.execute("select * from stocks limit 1;")
        return False
    except:
        return True


if db_is_empty():
    print("No database founded.")
    init_db()
