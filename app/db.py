import os
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={"autocommit": True},
    min_size=1,
    max_size=10
)

def get_conn():
    return pool.connection()

