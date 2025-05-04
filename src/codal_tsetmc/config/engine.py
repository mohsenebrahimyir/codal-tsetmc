from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
# is neccesary
from sqlalchemy import *
from pathlib import Path
import os
import sys
import logging
import yaml


def in_venv():
    return sys.prefix != sys.base_prefix


if in_venv():
    HOME_PATH = str(Path(sys.prefix).parent)
else:
    HOME_PATH = str(Path.home())

CDL_TSE_FOLDER = ".cdl_tse"
CONFIG_PATH = f"{os.path.join(HOME_PATH, CDL_TSE_FOLDER)}/config.yml"
FINGERPRINT_PATH = f"{os.path.join(HOME_PATH, CDL_TSE_FOLDER)}/fingerprint.txt"


def create_config():
    # create config.yml from config.default.yml
    path = os.path.join(HOME_PATH, CDL_TSE_FOLDER)
    if not os.path.exists(path):
        os.mkdir(path)
    if not os.path.exists(CONFIG_PATH):
        with open(
            os.path.join(os.path.dirname(__file__), "config.default.yml"), "r"
        ) as file:
            cfg = yaml.full_load(file)
        with open(CONFIG_PATH, "w") as file:
            yaml.dump(cfg, file)


create_config()

with open(CONFIG_PATH, "r") as f:
    config = yaml.full_load(f)


license_key = config.get("config").get("token").get("license_key")

default_db_path = os.path.join(
    f"{HOME_PATH}/{CDL_TSE_FOLDER}/companies-stocks.db"
)

db_path = config.get("config").get("database").get("path")
if db_path is None:
    db_path = default_db_path

default_engine_URI = f"sqlite:///{db_path}"
engine = config.get("config").get("database").get("engine")
if engine == "sqlite":
    engine_URI = default_engine_URI
else:
    engine = config.get("config").get("database").get("engine")
    host = config.get("config").get("database").get("host")
    port = config.get("config").get("database").get("port")
    database = config.get("config").get("database").get("database")
    user = config.get("config").get("database").get("user")
    password = config.get("config").get("database").get("password")
    engine_URI = f"{engine}://{user}:{password}@{host}:{port}/{database}"

logging.info(engine_URI)
engine = create_engine(engine_URI)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


class ClassProperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

    def __repr__(self):
        return None


class QueryMixin:
    @ClassProperty
    def query(self):
        return session.query(self)

    def display(self):
        data = self.__dict__
        try:
            del data["_sa_instance_state"]
        except Exception as e:
            print(e)

        return data


Base = declarative_base(cls=QueryMixin)
