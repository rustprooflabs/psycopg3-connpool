# psycopg3-connpool test

Simple Flask webapp to implement / test functionality and performance of
the new psycopg3 connection pool.

See: https://www.psycopg.org/psycopg3/docs/advanced/pool.html

Assuming Python 3.7+

```bash
cd ~/venv/
python -m venv psycopg3
source ~/venv/psycopg3/bin/activate
pip install -r requirements.txt
```



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
APP_DEBUG=True
```

Run Flask webapp, provide the env var to the script.

```bash
env $(cat ~/.psycopg3-connpool.env | grep -v ^# | xargs) python run_server.py
```


## Locust tests

Run w/ GUI.

```bash
locust -f locustfiles/pool_users.py
```


Headless, uses the shape defined in the locust file.

```bash
mkdir locust_out

locust --headless --only-summary \
    -H http://127.0.0.1:5000 \
    --html locust_out/pool_reporting.html \
    -f locustfiles/pool_users.py
```



## Setup for tests

```bash
sudo su - postgres
dropdb bench_test
createdb bench_test
pgbench -i -s 100 bench_test
```


Baseline test.  Setting thread count (`-j 2`) to `# CPU / 2`.  Client count = 5 per thread.
Run wide open and get rough expectation for TPS and latency ballpark.

```bash
pgbench -c 10 -j 2 -T 600 bench_test
```

Results from Digital Ocean droplet w/ 4 AMD CPU and 8 GB RAM, SSDs.

```
starting vacuum...end.

transaction type: <builtin: TPC-B (sort of)>
scaling factor: 100
query mode: simple
number of clients: 10
number of threads: 2
duration: 600 s
number of transactions actually processed: 2260097
latency average = 2.652 ms
latency stddev = 1.212 ms
tps = 3766.762091 (including connections establishing)
tps = 3766.782316 (excluding connections establishing)
```


Recreate.

```bash
dropdb bench_test
createdb bench_test
pgbench -i -s 100 bench_test
```

**WARNING:  Only run this on a TEST system!!!**

Remove log files to setup pgBadger report to only have the following pgbench test.

```
sudo rm /var/log/postgresql/postgresql-14-main.log*
sudo systemctl restart postgresql
```


PgBadger reports created with:


```
mkdir pgbadger
```

```bash
pgbadger --anonymize /var/log/postgresql/postgresql-14-main.log* -o pgbadger/test_name.html
```


