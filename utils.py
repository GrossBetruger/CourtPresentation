import psycopg2


def get_engine():
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password=''")
    return conn
