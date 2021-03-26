import logging
import psycopg3
import psycopg3.pool
import threading
import time
from random import random
from webapp import app, config


pool_default = psycopg3.pool.ConnectionPool(config.DATABASE_STRING,
                                            min_size=config.min_size,
                                            max_size=config.max_size,
                                            max_idle=config.max_idle)

def pool_stats():
    return pool_default.get_stats()


def get_data(sql_raw, params=None, single_row=False):
    """Main query point for all read queries.
    """
    if single_row:
        return _select_one(sql_raw, params)
    else:
        return _select_multi(sql_raw, params)


def _select_one(sql_raw, params):
    """ Runs SELECT query that will return zero or 1 rows.
    `params` is required but can be set to None if a LIMIT 1 is used.

    Parameters
    --------------------
    sql_raw : str
        Query string to execute.

    params : dict
        Parameters to pass into `sql_raw`

    Returns
    --------------------
    results
    """
    results = _execute_query(sql_raw, params, 'sel_single')
    return results


def insert(sql_raw, params):
    """ Runs Insert query, returns result.

    Returned result is typically the newly created PRIMARY KEY value from the database.
    """
    return _execute_query(sql_raw, params, 'insert')


def update(sql_raw, params):
    """ Runs UPDATE query, returns result depending on update query executed."""
    return _execute_query(sql_raw, params, 'update')


def _select_multi(sql_raw, params=None):
    """ Runs SELECT query that will return multiple (all) rows.

    Parameters
    --------------------
    sql_raw : str
        Query string to execute.

    params : dict
        (Optional) Parameters to pass into `sql_raw`

    Returns
    --------------------
    results
    """
    results = _execute_query(sql_raw, params, 'sel_multi')
    return results




def _execute_query(sql_raw, params, qry_type):
    """ Handles executing queries based on the `qry_type` passed in.

    Returns False if there are errors during connection or execution.

        if results == False:
            print('Database error')
        else:
            print(results)

    You cannot use `if not results:` b/c 0 results is a false negative.

    Parameters
    ---------------------
    sql_raw : str
        Query string to execute.

    params : dict
        (Optional) Parameters to pass into `sql_raw`

    qry_type : str
        Defines how the query is executed. e.g. `sel_multi`
        uses `.fetchall()` while `sel_single` uses `.fetchone()`.
    """
    app.logger.debug('Only the pool_default is configured!')
    with pool_default.connection() as conn:
        try:
            if qry_type == 'sel_multi':
                results = conn.execute(sql_raw, params).fetchall()
            elif qry_type == 'sel_single':
                results = conn.execute(sql_raw, params).fetchone()
            elif qry_type == 'insert':
                conn.execute(sql_raw, params)
                conn.commit()
                results = True
            elif qry_type == 'update':
                conn.execute(sql_raw, params)
                conn.commit()
                results = True
            else:
                raise Exception('Invalid query type defined.')
        except psycopg3.OperationalError as err:
            app.logger.error(f'Error querying: {err}')
        except psycopg3.ProgrammingError as err:
            app.logger.error('Database error via psycopg3.  %s', err)
            results = False
        except psycopg3.IntegrityError as err:
            app.logger.error('PostgreSQL integrity error via psycopg3.  %s', err)
            results = False

    return results




def _create_log_table():
    sql_raw = """CREATE TABLE IF NOT EXISTS public.psycopg3_pool_log
(id BIGSERIAL NOT NULL PRIMARY KEY, ts TIMESTAMPTZ NOT NULL DEFAULT NOW(), 
connections_num BIGINT,
connections_ms BIGINT,
requests_num BIGINT,
usage_ms BIGINT,
requests_queued BIGINT,
requests_wait_ms BIGINT,
pool_min BIGINT,
pool_max BIGINT,
pool_size BIGINT,
pool_available BIGINT,
requests_waiting BIGINT
)
"""
    insert(sql_raw, None)


def _monitor_pool(sleep_s=15):
    _create_log_table()

    sql_raw = """INSERT INTO public.psycopg3_pool_log (connections_num, connections_ms,
    requests_num, usage_ms, requests_queued, requests_wait_ms, pool_min, pool_max,
    pool_size, pool_available, requests_waiting)
VALUES (
    %(connections_num)s, %(connections_ms)s, %(requests_num)s, %(usage_ms)s,
    %(requests_queued)s, %(requests_wait_ms)s, %(pool_min)s, %(pool_max)s,
    %(pool_size)s, %(pool_available)s, %(requests_waiting)s
);
"""
    while True:
        stats = pool_stats()
        insert(sql_raw, params=stats)
        app.logger.info('DB Pool stats: %s', stats)
        time.sleep(sleep_s)

pool_thread = threading.Thread(target=_monitor_pool)
pool_thread.start()
