import psycopg2
from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display


def get_engine():
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password=''")
    return conn


def normalize_hebrew(raw_text: str):
    return get_display(arabic_reshaper.reshape(raw_text))