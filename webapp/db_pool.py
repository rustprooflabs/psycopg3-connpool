from collections import defaultdict
import logging
import psycopg
import psycopg_pool
import threading
import time
from random import random
from webapp import app, config


pool_default = psycopg_pool.ConnectionPool(config.DATABASE_STRING,
                                            min_size=config.POOL_MIN_SIZE,
                                            max_size=config.POOL_MAX_SIZE,
                                            max_idle=config.POOL_MAX_IDLE)

pool_reporting = psycopg_pool.ConnectionPool(config.DATABASE_STRING,
                                              min_size=0,
                                              max_size=5,
                                              max_idle=config.POOL_MAX_IDLE,
                                              timeout=120)


def pool_stats(pool_name='default'):
    """Returns the appropriate pool's stats. Uses `pop` to reset each time.

    Parameters
    -------------------------
    pool_name : str

    Returns
    -------------------------
    stats : defaultdict
    """
    if pool_name == 'reporting':
        stats_base = pool_reporting.pop_stats()
    else:
        stats_base = pool_default.pop_stats()

    stats = defaultdict(int, stats_base)
    stats['app_name'] = f'{config.APP_NAME}-{pool_name}'
    return stats


def get_data(sql_raw, params=None, single_row=False, pool_name='default'):
    """Main query point for all read queries.
    """
    if single_row:
        return _select_one(sql_raw, params)
    else:
        return _select_multi(sql_raw, params, pool_name=pool_name)


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


def _select_multi(sql_raw, params=None, pool_name='default'):
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
    results = _execute_query(sql_raw, params, 'sel_multi', pool_name=pool_name)
    return results


def _execute_query(sql_raw, params, qry_type, pool_name='default'):
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
    if pool_name == 'reporting':
        sel_pool = pool_reporting
    else:
        sel_pool = pool_default

    with sel_pool.connection() as conn:
        cur = conn.cursor(row_factory=psycopg.rows.dict_row)

        try:
            if qry_type == 'sel_multi':
                results = cur.execute(sql_raw, params).fetchall()
            elif qry_type == 'sel_single':
                results = cur.execute(sql_raw, params).fetchone()
            elif qry_type == 'insert':
                cur.execute(sql_raw, params)
                conn.commit()
                results = True
            elif qry_type == 'update':
                cur.execute(sql_raw, params)
                conn.commit()
                results = True
            else:
                raise Exception('Invalid query type defined.')
        except psycopg.OperationalError as err:
            app.logger.error(f'Error querying: {err}')
        except psycopg.ProgrammingError as err:
            app.logger.error('Database error via psycopg.  %s', err)
            results = False
        except psycopg.IntegrityError as err:
            app.logger.error('PostgreSQL integrity error via psycopg.  %s', err)
            results = False

    return results




def _create_log_table():
    sql_raw = """CREATE TABLE IF NOT EXISTS public.psycopg3_pool_log
(
    id BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    app_name TEXT NULL,
    pool_min BIGINT,
    pool_max BIGINT,
    pool_size BIGINT,
    pool_available BIGINT,
    requests_waiting BIGINT,
    usage_ms BIGINT,
    requests_num BIGINT,
    requests_queued BIGINT,
    requests_wait_ms BIGINT,
    requests_errors BIGINT,
    returns_bad BIGINT,
    connections_num BIGINT,
    connections_ms BIGINT,
    connections_errors BIGINT,
    connections_lost BIGINT
)
"""
    insert(sql_raw, None)


def _monitor_pool(sleep_s=config.POOL_STAT_SLEEP):
    _create_log_table()

    sql_raw = """INSERT INTO public.psycopg3_pool_log
        (pool_min, pool_max, pool_size, pool_available, requests_waiting, usage_ms,
        requests_num, requests_queued, requests_wait_ms, requests_errors, returns_bad,
        connections_num, connections_ms, connections_errors, connections_lost,
        app_name)
VALUES (
        %(pool_min)s, %(pool_max)s, %(pool_size)s, %(pool_available)s, %(requests_waiting)s,
        %(usage_ms)s, %(requests_num)s, %(requests_queued)s, %(requests_wait_ms)s,
        %(requests_errors)s, %(returns_bad)s, %(connections_num)s, %(connections_ms)s,
        %(connections_errors)s, %(connections_lost)s,
        %(app_name)s
);
"""
    while True:
        stats = pool_stats()
        insert(sql_raw, params=stats)
        app.logger.info('DB Pool stats: %s', stats)

        stats = pool_stats('reporting')
        insert(sql_raw, params=stats)
        app.logger.info('DB Reporting Pool stats: %s', stats)

        time.sleep(sleep_s)

pool_thread = threading.Thread(target=_monitor_pool)
pool_thread.start()
