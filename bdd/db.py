import psycopg2 as pg
from psycopg2.extras import NamedTupleCursor
import os
from dotenv import load_dotenv

load_dotenv()

def connect():
    conn = pg.connect(
        user="elazar",
        password=os.getenv('DB_PASSWORD'),
        dbname="tuteure",
        host="localhost",
        port=5432,
        cursor_factory=NamedTupleCursor
    )
    conn.autocommit = True
    return conn
