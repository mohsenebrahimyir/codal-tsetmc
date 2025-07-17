from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
# is neccesary
from sqlalchemy import *
from dotenv import load_dotenv
from pathlib import Path
import os
import sys
import logging
import yaml


def in_venv():
    return sys.prefix != sys.base_prefix


def has_env_vars():
    return any(
        os.getenv(var)
        for var in [
            "CDL_TSE_DATABASE_ENGINE",
            "CDL_TSE_DATABASE_HOST",
            "CDL_TSE_DATABASE_PORT",
            "CDL_TSE_DATABASE_DB",
            "CDL_TSE_DATABASE_USER",
            "CDL_TSE_DATABASE_PASS",
            "CDL_TSE_LICENSE_KEY",
        ]
    )

load_dotenv()

if in_venv():
    HOME_PATH = str(Path(sys.prefix).parent)
else:
    HOME_PATH = str(Path.home())

CDL_TSE_FOLDER = ".cdl_tse"
CONFIG_PATH = f"{os.path.join(HOME_PATH, CDL_TSE_FOLDER)}/config.yml"
GITIGNORE_PATH = f"{os.path.join(HOME_PATH, CDL_TSE_FOLDER)}/.gitignore"


def create_config():
    if has_env_vars():
        return
    
    # create config.yml from config.default.yml
    path = os.path.join(HOME_PATH, CDL_TSE_FOLDER)
    if not os.path.exists(path):
        os.mkdir(path)
    if not os.path.exists(GITIGNORE_PATH):
        with open(GITIGNORE_PATH, "w") as file:
            file.write("*")
    if not os.path.exists(CONFIG_PATH):
        with open(
            os.path.join(os.path.dirname(__file__), "config.default.yml"), "r"
        ) as file:
            cfg = yaml.full_load(file)
        with open(CONFIG_PATH, "w") as file:
            yaml.dump(cfg, file)


create_config()


def get_config_value(env_var, config_path, default=None):
    """Get value from env or config file with fallback to default"""
    value = os.getenv(env_var)
    if value is not None:
        return value

    try:
        with open(CONFIG_PATH, "r") as f:
            config = yaml.full_load(f)
            # Navigate through nested dictionary using config_path
            keys = config_path.split(".")
            result = config
            for key in keys:
                result = result.get(key, {})
            return result or default
    except (FileNotFoundError, yaml.YAMLError):
        return default


license_key = get_config_value("CDL_TSE_LICENSE_KEY", "config.token.license_key")


db_config = {
    "engine": get_config_value(
        "CDL_TSE_DATABASE_ENGINE", "config.database.engine", "sqlite"
    ),
    "path": get_config_value("CDL_TSE_DATABASE_PATH", "config.database.path"),
    "host": get_config_value("CDL_TSE_DATABASE_HOST", "config.database.host"),
    "port": get_config_value("CDL_TSE_DATABASE_PORT", "config.database.port"),
    "database": get_config_value("CDL_TSE_DATABASE_DB", "config.database.database"),
    "user": get_config_value("CDL_TSE_DATABASE_USER", "config.database.user"),
    "password": get_config_value("CDL_TSE_DATABASE_PASS", "config.database.password"),
}

# Determine database URL
if db_config["engine"] == "sqlite":
    default_db_path = os.path.join(f"{HOME_PATH}/{CDL_TSE_FOLDER}/companies-stocks.db")
    db_path = db_config["path"] or default_db_path
    engine_URI = f"sqlite:///{db_path}"
else:
    engine_URI = f"{db_config['engine']}://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

logging.info(f"Database URI: {engine_URI}")
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
