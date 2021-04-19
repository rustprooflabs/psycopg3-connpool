"""Uses queries against the standard pgbench tables.

Some based around queries in docs (https://www.postgresql.org/docs/current/pgbench.html)
others more geared toward "real" types of queries.
"""
from webapp import app, db, db_pool


def get_account_balance(account_id, pool):
    """Returns the account balance for `account_id`

    Parameters
    ------------------
    account_id : int
    pool : str
        To pool or not to pool?

    Returns
    ------------------
    account_balance : int
    """
    sql_raw = 'SELECT * FROM pgbench_accounts WHERE aid = %(account_id)s ;'
    params = {'account_id': account_id}

    if pool == 'pool':
        data = db_pool.get_data(sql_raw, params, single_row=True)
    else:
        data = db.get_data(sql_raw, params, single_row=True)

    account_balance = data['abalance']
    return account_balance


def update_account_balance(account_id, delta, pool):
    """Runs three `UPDATE` and one `INSERT` query, each in their own transaction.

    WARNING: A real banking app would put all these queries in one transaction.
    The purpose of this project is to test the impact of creating connections,
    this approach intentionally adds stress to that aspect.

    Parameters
    ------------------
    account_id : int
    delta : int
    pool : str
        To pool or not to pool?

    Returns
    ------------------
    account_balance : int
    """
    qry1 = """
UPDATE pgbench_accounts
    SET abalance = abalance + %(delta)s
    WHERE aid = %(account_id)s
;
"""
    qry2 = """
UPDATE pgbench_tellers
    SET tbalance = tbalance + %(delta)s WHERE tid = 1;
"""

    qry3 = """
UPDATE pgbench_branches SET bbalance = bbalance + %(delta)s WHERE bid = 1;
"""

    qry4 = """
INSERT INTO pgbench_history (tid, bid, aid, delta, mtime) 
    VALUES (1, 1, %(account_id)s, %(delta)s, now());
"""

    params_both = {
        'account_id': account_id,
        'delta': delta
    }
    params_single = {
        'delta': delta
    }

    if pool == 'pool':
        results1 = db_pool.update(qry1, params_both)
        results2 = db_pool.update(qry2, params_single)
        results3 = db_pool.update(qry3, params_single)
        results4 = db_pool.insert(qry4, params_both)
    else:
        results1 = db.update(qry1, params_both)
        results2 = db.update(qry2, params_single)
        results3 = db.update(qry3, params_single)
        results4 = db.insert(qry4, params_both)
    return [results1, results2, results3, results4]


def get_recent_activity_by_branch(pool):
    sql_raw = """
SELECT 1 AS sort, '1 minute' AS time_frame, bid, COUNT(*) AS account_updates,
        COUNT(DISTINCT aid) AS active_accounts,
        SUM(delta) sum_of_deltas
    FROM public.pgbench_history
    WHERE now() AT TIME ZONE 'UTC'- mtime  < '1 minute'::INTERVAL
    GROUP BY bid
UNION
SELECT 2 AS sort, '1 hour' AS time_frame, bid, COUNT(*) AS account_updates,
        COUNT(DISTINCT aid) AS active_accounts,
        SUM(delta) sum_of_deltas
    FROM public.pgbench_history
    WHERE now() AT TIME ZONE 'UTC'- mtime  < '1 hour'::INTERVAL
    GROUP BY bid
UNION
SELECT 3 AS sort, '1 day' AS time_frame, bid, COUNT(*) AS account_updates,
        COUNT(DISTINCT aid) AS active_accounts,
        SUM(delta) sum_of_deltas
    FROM public.pgbench_history
    WHERE now() AT TIME ZONE 'UTC'- mtime  < '1 day'::INTERVAL
    GROUP BY bid
    ORDER BY sort, bid
;
"""

    if pool == 'pool':
        results = db_pool.get_data(sql_raw, params=None)
    else:
        results = db.get_data(sql_raw, params=None)
    return results



def get_branch_stats(pool, branch_id):
    sql_raw = """
SELECT COUNT(*) AS accounts,
        MIN(abalance), AVG(abalance)::FLOAT8, MAX(abalance), SUM(abalance)
    FROM public.pgbench_accounts
    WHERE bid = %(branch_id)s
;
"""
    params = {'branch_id': branch_id}

    if pool == 'pool':
        results = db_pool.get_data(sql_raw, params=params)
    else:
        results = db.get_data(sql_raw, params=params)
    return results



def get_teller_balance(teller_id):
    pass


def update_branch_balance(branch_id):
    pass


def update_teller_balance(teller_id):
    pass


def get_account_last_10_transactions(account_id):
    pass

