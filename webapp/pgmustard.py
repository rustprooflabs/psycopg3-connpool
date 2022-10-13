import datetime
import requests
import threading
from webapp import config, db_pool


def tracker(sql_raw, params, qry_type, pool_name):
    """Occasionally re-runs queries with EXPLAIN (ANALYZE) to
    submit to pgMustard.
    """
    if config.PGMUSTARD_PW is None:
        return

    # Insert/update don't expect returns, currently not supported
    invalid_types = ['insert', 'update']
    if qry_type in invalid_types:
        return

    if config.PGMUSTARD_COUNTER < config.PGMUSTARD_FREQUENCY:
        config.PGMUSTARD_COUNTER += 1
        print(config.PGMUSTARD_COUNTER)
    else:
        print('resetting pgmustard counter')
        config.PGMUSTARD_COUNTER = 0

        args = [sql_raw, params, qry_type, pool_name]
        pool_thread = threading.Thread(target=explain_with_pgmustard,
                                       args=args)
        pool_thread.start()

        #explain_with_pgmustard()


def explain_with_pgmustard(sql_raw, params, qry_type, pool_name):
    plan = run_with_explain(sql_raw, params, qry_type, pool_name)
    #print(plan)
    query_id = plan['Query Identifier']
    if query_id in config.KNOWN_QUERIES:
        # Currently it doesn't matter why it's known
        known_query = config.KNOWN_QUERIES[query_id]
        print(f'Known query: {known_query}')
        known_age = datetime.datetime.now() - known_query['observed_at']
        age_seconds = known_age.total_seconds()

        if age_seconds > config.KNOWN_QUERY_CACHE_MAX_AGE:
            config.KNOWN_QUERIES.pop(query_id)
        return

    min_query_time = config.PGMUSTARD_MIN_THRESHOLD_MS
    if plan['Execution Time'] < min_query_time:
        print('Fast query, not sending to pgMustard')
        known_query = {'fast': True, 'pgmustard-results': None,
                       'observed_at': datetime.datetime.now()}
        config.KNOWN_QUERIES[query_id] = known_query
        return True

    pgmustard_results = pgmustard_api(plan)
    print(sql_raw)
    query_id = pgmustard_results['query-identifier']
    print(query_id)

    # 10% longer than minimum
    if pgmustard_results['query-time'] <= min_query_time * .1:
        print('Query is still fast...')
        known_query = {'fast': True, 'pgmustard-results': pgmustard_results,
                       'observed_at': datetime.datetime.now()}
        config.KNOWN_QUERIES[query_id] = known_query
        return True

    print(f'Query took longer than {min_query_time}, logging pgMustard results')

    log_pgmustard_results(pgmustard_results)


def run_with_explain(sql_raw, params, qry_type, pool_name):
    """Run query with most verbose explain analyze settings for pgMustard.
    """
    explain_txt = 'EXPLAIN (ANALYZE, BUFFERS, WAL, SETTINGS, VERBOSE, FORMAT JSON) '
    sql_w_explain = explain_txt + sql_raw
    output = db_pool._execute_query(sql_w_explain, params, qry_type, pool_name)
    return output['QUERY PLAN'][0]


def pgmustard_api(plan):
    print('Sending plan to pgMustard')

    pgmustard_uri = 'https://app.pgmustard.com/api/v1/analyze'
    method = 'POST'
    observation = {'plan': plan,
                   'password': config.PGMUSTARD_PW
                    }
    response = requests.request(method=method,
                                url=pgmustard_uri,
                                json=observation)

    pgmustard_results = response.json()
    return pgmustard_results


def log_pgmustard_results(pgmustard_results):
    known_query = {'fast': False, 'pgmustard-results': pgmustard_results,
                   'observed_at': datetime.datetime.now()}
    query_id = pgmustard_results['query-identifier']
    config.KNOWN_QUERIES[query_id] = known_query

    print(pgmustard_results)


