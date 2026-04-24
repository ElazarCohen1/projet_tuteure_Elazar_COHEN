import psycopg2 as pg
from psycopg2.extras import NamedTupleCursor
import os
from dotenv import load_dotenv

load_dotenv()


_password = os.getenv("DB_PASSWORD")
if not _password:
    raise EnvironmentError("La variable d'environnement DB_PASSWORD n'est pas définie.")
 
 
def connect():
    conn = pg.connect(
        user="elazar",
        password=_password,
        dbname="tuteure",
        host="localhost",
        port=5432,
        cursor_factory=NamedTupleCursor
    )
    conn.autocommit = True
    return conn
 