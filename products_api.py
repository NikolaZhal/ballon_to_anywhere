import flask
from flask import request, jsonify, abort, redirect
from data import db_session
from flask import session
from data.products import Products
from data.balloon_types import Types
from data.users import User
from data.orders import Order
import ast


blueprint = flask.Blueprint(
    'ballons_api',
    __name__,
    template_folder='templates'
)
@blueprint.route('/api/add_product', methods=['POST'])
def add_product():
    data = request.json
    product_id = data['product_id']
    user_id = data['user_id']
    href = data['href']
    if user_id == 0:
        return redirect('/login')
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
        return redirect('/login')
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
        return redirect('/login')
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