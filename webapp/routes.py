from flask import (render_template, abort, request, jsonify, Response)
from webapp import app, db

@app.route('/')
def conn_pool_fast_query():
    """Fastest query time"""
    data = db.query(scale=0.0)
    return jsonify(success='True', data=data[0])


@app.route('/<scale>')
def conn_pool_scale_query_speed(scale):
    """Fastest query time"""
    data = db.query(scale=float(scale))
    return jsonify(success='True', data=data[0])

