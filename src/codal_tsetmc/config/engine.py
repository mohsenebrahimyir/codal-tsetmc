import contextlib
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from pathlib import Path
import os
import logging
import yaml


HOME_PATH = str(Path.home())
CDL_TSE_FOLDER = ".cdl_tse"
CONFIG_PATH = f"{os.path.join(HOME_PATH, CDL_TSE_FOLDER)}/config.yml"


def create_config():
    # create config.yml from config.default.yml
    if not os.path.exists(CONFIG_PATH):
        with open(os.path.join(os.path.dirname(__file__), "config.default.yml"), "r") as f:
            config = yaml.full_load(f)
        with contextlib.suppress(FileExistsError):
            path = os.path.join(HOME_PATH, CDL_TSE_FOLDER)
            os.mkdir(path)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(config, f)


create_config()


with open(CONFIG_PATH, "r") as f:
    config = yaml.full_load(f)

default_db_path = os.path.join(f"{HOME_PATH}/{CDL_TSE_FOLDER}/companies-stocks.db")

db_path = config.get("database").get("path")
if db_path is None:
    db_path = default_db_path

default_engine_URI = f"sqlite:///{db_path}"
engine = config.get("database").get("engine")
if engine == "sqlite":
    engine_URI = default_engine_URI
else:
    engine = config.get("database").get("engine")
    host = config.get("database").get("host")
    port = config.get("database").get("port")
    database = config.get("database").get("database")
    user = config.get("database").get("user")
    password = config.get("database").get("password")
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
    def query(cls):
        return session.query(cls)

    def display(self):
        data = self.__dict__
        try:
            del data["_sa_instance_state"]
        except Exception as e:
            print(e)
        finally:
            pass

        return data


Base = declarative_base(cls=QueryMixin)
