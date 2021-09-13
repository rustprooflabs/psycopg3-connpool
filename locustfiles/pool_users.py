import time
import random
from locust import HttpUser, task, between, LoadTestShape
import locust_config as lc

ACCOUNT_ID_MAX = 100000 * lc.BENCH_SCALE
print(f'Account Max ID: {ACCOUNT_ID_MAX}')

if lc.USE_POOL:
    print('Using DB Pool paths')
    pool_str = 'pool'
else:
    print('Not using DB Pool paths')
    pool_str = 'nopool'


class BankWebappUser(HttpUser):
    wait_time = between(1, 3.5)
    weight = 75

    @task(5)
    def check_balance(self):
        account_id = random.randint(1, ACCOUNT_ID_MAX)
        self.client.get(f'/{pool_str}/account/{account_id}', name=f'{pool_str}: account_balance')

    @task(1)
    def update_balance(self):
        account_id = random.randint(1, ACCOUNT_ID_MAX)
        delta = random.randint(-100, 200)

        # check account 1st
        self.client.get(f'/{pool_str}/account/{account_id}', name=f'{pool_str}: account_balance')
        # Update
        self.client.get(f'/{pool_str}/account/{account_id}/update/{delta}', name=f'{pool_str}: account_update')

class ReportingUser(HttpUser):
    wait_time = between(1.5, 6)

    @task(5)
    def view_branch_activity(self):
        self.client.get(f'/{pool_str}/report/branch_activity', name=f'{pool_str}: report branch activity')

    @task(1)
    def view_branch_1_report(self):
        self.client.get(f'/{pool_str}/report/branch/1', name=f'{pool_str}: report branch 1')




# class StagesShape(LoadTestShape):
#     """
#     Based on: https://github.com/locustio/locust/blob/master/examples/custom_shape/stages.py

#     A simply load test shape class that has different user and spawn_rate at
#     different stages.
#     Keyword arguments:
#         stages -- A list of dicts, each representing a stage with the following keys:
#             duration -- When this many seconds pass the test is advanced to the next stage
#             users -- Total user count
#             spawn_rate -- Number of users to start/stop per second
#             stop -- A boolean that can stop that test at a specific stage
#         stop_at_end -- Can be set to stop once all stages have run.
#     """

#     stages = [
#         {"duration": 20, "users": 25, "spawn_rate": 2},
#         {"duration": 80, "users": 75, "spawn_rate": 10},
#         {"duration": 120, "users": 10, "spawn_rate": 4},
#         {"duration": 200, "users": 120, "spawn_rate": 25},
#         {"duration": 230, "users": 50, "spawn_rate": 4},
#         {"duration": 250, "users": 3, "spawn_rate": 1},
#     ]

#     def tick(self):
#         run_time = self.get_run_time()

#         for stage in self.stages:
#             if run_time < stage["duration"]:
#                 tick_data = (stage["users"], stage["spawn_rate"])
#                 return tick_data

#         return None
