import flask
from flask import request, jsonify, make_response
from data import db_session
from flask import session
from data.products import Products
from data.types import Types
from data.users import User
from data.orders import Order
import ast


blueprint = flask.Blueprint(
    'ballons_api',
    __name__,
    template_folder='templates'
)
@blueprint.route('/api/products')
def get_news():
    db_sess = db_session.create_session()
    news = db_sess.query(Products).all()
    return jsonify(
        {
            'news':
                [item.to_dict(only=('title', 'content', 'user.name'))
                 for item in news]
        }
    )

@blueprint.route('/api/add_product', methods=['POST'])
def add_product():
    data = request.json
    product_id = data['product_id']
    user_id = data['user_id']
    if user_id == 0:
        if product_id not in session['basket']:
            session['basket'][product_id] = 0
        session['basket'][product_id] += 1
        print(session.get('basket'))
    else:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        user.basket = ast.literal_eval(user.basket)
        if product_id not in user.basket:
            user.basket[product_id] = 0
        user.basket[product_id] += 1
        user.basket = str(user.basket)
        db_sess.commit()

    # db_sess.commit()
    return jsonify(request.json)

@blueprint.route('/api/minus_product', methods=['POST'])
def minus_product():
    data = request.json
    product_id = data['product_id']
    user_id = data['user_id']
    if user_id == 0:
        if product_id not in session['basket']:
            session['basket'][product_id] = 0
        session['basket'][product_id] += 1
        print(session.get('basket'))
    else:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        user.basket = ast.literal_eval(user.basket)
        if product_id not in user.basket:
            return jsonify(request.json)
        if user.basket[product_id] != 1:
            user.basket[product_id] -= 1
        user.basket = str(user.basket)
        db_sess.commit()
    return jsonify(request.json)


@blueprint.route('/api/remove_product', methods=['POST'])
def remove_product():
    data = request.json
    product_id = data['product_id']
    user_id = data['user_id']
    if user_id == 0:
        ...
    else:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == user_id).first()
        user.basket = ast.literal_eval(user.basket)
        if product_id not in user.basket:
            return jsonify(request.json)
        del user.basket[product_id]
        user.basket = str(user.basket)
        db_sess.commit()
    return jsonify(request.json)