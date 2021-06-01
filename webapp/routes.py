"""psycopg3-connpool test webapp routes.
"""
import logging
from flask import render_template, abort, request, jsonify, Response
from webapp import app, bank, db_pool


@app.route('/pool_stats')
@app.route('/pool_stats/<pool_name>')
def view_db_pool_stats(pool_name='default'):
    data = db_pool.pool_stats(pool_name=pool_name)
    return jsonify(success='True', data=data)


@app.route('/<pool>/account/<account_id>')
def view_get_account_balance(pool, account_id):
    account_balance = bank.get_account_balance(account_id, pool)
    return jsonify(success='True', account_balance=account_balance)


@app.route('/<pool>/account/<account_id>/update/<delta>')
def view_update_account_balance(pool, account_id, delta):
    update_results = bank.update_account_balance(account_id, delta, pool)
    account_balance = bank.get_account_balance(account_id, pool)

    app.logger.debug('Update results: %s', update_results)
    return jsonify(success='True',
                   update_results=update_results,
                   account_balance=account_balance)

@app.route('/<pool>/report/branch_activity')
def view_report_branch_activity(pool):
    data = bank.get_recent_activity_by_branch(pool)
    return jsonify(success='True',
                   data=data)

@app.route('/<pool>/report/branch/<branch_id>')
def view_report_branch_stats(pool, branch_id):
    data = bank.get_branch_stats(pool, branch_id)
    return jsonify(success='True',
                   data=data)

