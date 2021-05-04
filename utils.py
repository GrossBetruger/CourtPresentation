import os

import psycopg2
from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display

PGPASS = "~/.pgpass"


def read_password() -> str:
    try:
        assert os.path.exists(os.path.expanduser(PGPASS))
        return open(os.path.expanduser(PGPASS)).read().strip()
    except AssertionError:
        print(f"expected db password in: {PGPASS}")


def get_engine() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(f"dbname='postgres' user='postgres' host='localhost' password='{read_password()}'")
    return conn


def normalize_hebrew(raw_text: str):
    return get_display(arabic_reshaper.reshape(raw_text))