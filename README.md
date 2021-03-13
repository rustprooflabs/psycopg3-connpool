# psycopg3-connpool test

Simple Flask webapp to implement / test functionality and performance of
the new psycopg3 connection pool.

See: https://www.psycopg.org/psycopg3/docs/advanced/pool.html

Assuming Python 3.7+

Install `requirements.txt`.  Manually install psycopg3 (not in PyPI yet!)
See https://www.psycopg.org/psycopg3/docs/basic/install.html


```bash
touch ~/.psycopg3-connpool.env
chmod 0600 ~/.psycopg3-connpool.env
nano ~/.psycopg3-connpool.env
```

Run Flask webapp

```bash
env $(cat ~/.psycopg3-connpool.env | grep -v ^# | xargs) python run_server.py
```



