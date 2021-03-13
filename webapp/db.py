import psycopg3
import psycopg3.pool
from webapp import config

p = psycopg3.pool.ConnectionPool(config.DATABASE_STRING,
                                 min_size=config.min_size,
                                 max_size=config.max_size,
                                 max_idle=config.max_idle)


with p.connection() as conn:
    print(conn.execute("SELECT version();").fetchone())

from random import random

def query(scale=1.0):
    x = random() * scale
    sql_raw = 'SELECT %(x)s AS x FROM pg_sleep(%(x)s);'

    with p.connection() as conn:
        params = {'x': x}
        try:
            results = conn.execute(sql_raw, params).fetchone()
            return results
        except psycopg3.OperationalError as err:
            print(f'Error querying: {err}')
            
