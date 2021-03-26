import logging
from flask import render_template, abort, request, jsonify, Response
from webapp import app, bank, db_pool


@app.route('/pool_stats')
def view_db_pool_stats():
    data = db_pool.pool_stats()
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

