# psycopg3-connpool test

Simple Flask webapp to implement / test functionality and performance of
the new psycopg3 connection pool.

See: https://www.psycopg.org/psycopg3/docs/advanced/pool.html

Assuming Python 3.7+

```bash
cd ~/venv/
python -m venv psycopg3
source ~/venv/psycopg3/bin/activate
```


Install `requirements.txt`.  Manually install psycopg3 (not in PyPI yet!)
See https://www.psycopg.org/psycopg3/docs/basic/install.html


## Env vars

The webapp needs a Postgres connection string.  It can be set as an environment,
this persists it in the users' directory as a protected file (same premise as
`~/.pgpass`).


```bash
touch ~/.psycopg3-connpool.env
chmod 0600 ~/.psycopg3-connpool.env
nano ~/.psycopg3-connpool.env
```

Add your Postgres connection string to the ``.env`` file.  This example assumes a
`~/.pgpass` file is setup with the password, and the port is the default 5432.

```bash
PG_CONN=postgresql://your_user@db_host/test_db_name?application_name=psycopg3-connpool-webapp
```

Run Flask webapp, provide the env var to the script.

```bash
env $(cat ~/.psycopg3-connpool.env | grep -v ^# | xargs) python run_server.py
```



