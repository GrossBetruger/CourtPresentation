import os
import psycopg2

from typing import List, Optional
from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display
from sqlalchemy import create_engine

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


def get_sql_alchemy_engine():
    engine = create_engine(f'postgresql://postgres:{read_password()}@localhost:5432/postgres')
    return engine


def get_remote_engine() -> psycopg2.extensions.connection:
    print(os.environ.get('RDS_PASSWORD'))
    conn = psycopg2.connect(f"dbname='caseyellow' user='dango' "
                            f"host='caseyellow.cgqzew4kdsmr.eu-central-1.rds.amazonaws.com'"
                            f"password='{os.environ.get('RDS_PASSWORD')}'")
    return conn


def get_rows(read_only_query: str, args: Optional[tuple] = None) -> List[tuple]:
    conn = get_engine()
    cur = conn.cursor()

    cur.execute(read_only_query, args)
    rows = []
    for row in cur.fetchall():
        rows.append(row)
    return rows


def normalize_hebrew(raw_text: str):
    return get_display(arabic_reshaper.reshape(raw_text))