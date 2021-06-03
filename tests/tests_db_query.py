import psycopg2
from ..app import DB_HOST, DB_NAME, DB_PASS, DB_USER, req_table, don_table

def adds_elem_in_db():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    conn.commit()
    cur.close()
    conn.close()
