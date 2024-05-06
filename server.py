import ast
import os
from datetime import datetime
from os import listdir
from os.path import isfile, join
from random import randint

from flask import Flask
from flask import render_template, redirect, request, abort
from flask import session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import products_api
from bot import send_info
from data import db_session
from data.orders import Order
from data.products import Products
from data.products_group import ProductGroup
from data.types import Types
from data.users import User
from email_sender import send_email
from forms.orders import BasketForm, MakeOrder
from forms.products import ProductForm
from forms.types import TypeForm
from forms.user import RegisterForm, LoginForm, ConfirmationForm

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOAD_FOLDER = './static/img/upload'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Products).all()
    for product in products:
        if product.img:
            product.img = product.img.split(', ')
    session['basket'] = {}
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>', methods=['GET', 'POST'])
def show_product():
    return

@app.route('/admin/types', methods=['GET', 'POST'])
@login_required
def admin_types():
    if current_user.admin:
        filenames = ['']
        form = TypeForm()
        db_sess = db_session.create_session()
        types = db_sess.query(Types).all()

        if form.validate_on_submit():
            # добавление продукта
            type = Types()
            type.title = form.title.data
            form.title.data = ''
            db_sess = db_session.create_session()
            db_sess.add(type)
            db_sess.commit()
            return redirect('/admin/types')
        if request.method == "POST":
            db_sess = db_session.create_session()
            for id in request.form:
                type = db_sess.query(Types).filter(Types.id == id).first()
                type.title = request.form[id]
                db_sess.commit()
                # request.form[id] = ''
            return redirect('/admin/types')
        return render_template('admin_types.html', title='Админ панель',
                               types=types, form=form)


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_user():
    if current_user.admin:
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return render_template('admin_users.html', title='Админ панель',
                               users=users)


@app.route('/admin/orders', methods=['GET', 'POST'])
@login_required
def admin_orders():
    if current_user.admin:
        db_sess = db_session.create_session()
        orders = db_sess.query(Order).all()
        return render_template('admin_orders.html', title='Админ панель',
                               orders=orders)


@app.route('/admin/products', methods=['GET', 'POST'])
@login_required
def admin_products():
    if current_user.admin:
        db_sess = db_session.create_session()
        products = db_sess.query(Products).all()
        for product in products:
            if product.img:
                product.img = product.img.split(', ')
        return render_template('admin_products.html', title='Админ панель',
                               products=products)
    else:
        return render_template('no_rights.html')


@app.route('/remove_item/<string:type>/<int:id>', methods=['GET', 'POST'])
def remove_item(type, id):
    if current_user.admin:
        if type == 'products':
            db_sess = db_session.create_session()
            db_sess.query(Products).filter(Products.id == id).delete()
            db_sess.commit()
        return redirect('/admin/products')
    else:
        return render_template('no_rights.html')


@app.route('/admin/product', methods=['GET', 'POST'])
def add_product():
    data = []

    db_sess = db_session.create_session()
    types = db_sess.query(Types).all()
    types_data = []
    for i in types:
        types_data.append((i.id, i.title))
    types = db_sess.query(Types).all()
    types_data = []
    for i in types:
        types_data.append((i.id, i.title))
    form = ProductForm(types=types_data, prduct_group=[])
    # if request.method == 'POST':
    if form.validate_on_submit():
        filenames = ['']

        # добавление продукта
        product = Products()
        product.title = form.title.data
        product.description = form.description.data
        product.type = form.type.data
        product.sale = int(form.sale.data)
        product.special_offer = int(form.special_offer.data)
        product.cost = form.cost.data
        product.remains = form.remains.data
        product.img = str(form.img.data)
        db_sess = db_session.create_session()
        db_sess.add(product)
        db_sess.commit()
        product_id = product.id

        files_filenames = []
        for i, file in enumerate(form.img.data):
            data_filename = secure_filename(file.filename)
            data_filename = f"{product_id}_{i}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
            file.save(os.path.join('./static/img/products', data_filename))
            files_filenames.append(data_filename)
        db_sess = db_session.create_session()
        product = db_sess.query(Products).filter(Products.id == product_id).first()
        product.img = f'{", ".join(files_filenames)}'
        db_sess.commit()
        return redirect('/admin/products')

    mypath = "./static/img"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    data = {'change': '0'}
    return render_template("add_product.html", data=data, form=form)


@app.route('/admin/product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    db_sess = db_session.create_session()
    types = db_sess.query(Types).all()
    types_data = []

    # дописать нужны все файлы к данному product по id

    mypath = "./static/img/products"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    all_imgs = list(
        filter(lambda x: (x.endswith(".jpg") or x.endswith(".png")) and x.split('_')[0] == str(id), onlyfiles))

    max_img_number = 0
    if len(all_imgs):
        max_img_number = max(all_imgs, key=lambda z: int(z.split('_')[1]))
        max_img_number = int(max_img_number.split('_')[1]) + 1

    for i in types:
        types_data.append((i.id, i.title))
    db_sess = db_session.create_session()
    product = db_sess.query(Products).filter(Products.id == id).first()
    if product.img:
        product.img.split(', ')
    if product:
        choises = []
        if product.img:
            for elem in product.img:
                choises.append((elem, elem))
        form = ProductForm(types=types_data, imgs_data=all_imgs, type=int(product.type))
    if request.method == "GET":
        if product:
            form.title.data = product.title
            form.description.data = product.description
            form.type.data = product.type
            form.sale.data = product.sale
            form.special_offer.data = product.special_offer
            form.cost.data = product.cost
            form.imgs.data = product.img
            form.remains.data = product.remains
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = db_sess.query(Products).filter(Products.id == id).first()
        if product:
            product.title = form.title.data
            product.description = form.description.data
            product.type = form.type.data
            product.sale = form.sale.data
            product.special_offer = form.special_offer.data
            product.cost = form.cost.data
            product.remains = form.remains.data
            product.img = ', '.join(form.imgs.data)
            if form.img.data[0].filename != '':

                files_filenames = []
                for i, file in enumerate(form.img.data, start=max_img_number):
                    data_filename = secure_filename(file.filename)
                    data_filename = f"{id}_{i}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
                    file.save(os.path.join('./static/img/products', data_filename))
                    files_filenames.append(data_filename)
                if len(product.img):
                    product.img += f', {", ".join(files_filenames)}'
                else:
                    product.img += f'{", ".join(files_filenames)}'
            db_sess.commit()

            return redirect('/admin/products')
            # return str(form.img.data)
        else:
            abort(404)
    db_sess = db_session.create_session()
    product = db_sess.query(Products).filter(Products.id == id).first()
    data = {'change': '1', 'img': product.img}
    return render_template('add_product.html',
                           title='Редактирование новости',
                           form=form, data=data
                           )


@app.route('/make_order', methods=['GET', 'POST'])
@login_required
def user_make_order():
    content = {}
    first_content = session.get('order').get('content')
    to_order = session.get('order').get('to_order')
    for i in to_order:
        content[i] = first_content[i]
    form = MakeOrder()

    if form.validate_on_submit():
        date = datetime.fromisoformat(str(form.date.data) + 'T' + str(form.time.data))
        # time = datetime.strptime(str(form.time.data))
        db_sess = db_session.create_session()
        order = Order(
            content=str(content),
            user_id=current_user.id,
            to_date=date,
            data=form.description.data,
            address=form.address.data,
            how_pay=form.how_pay.data
        )
        db_sess.add(order)
        db_sess.commit()
        order.content = ast.literal_eval(order.content)
        message = make_order_text(order)
        db_sess = db_session.create_session()
        admins = db_sess.query(User).filter(User.admin == True).all()
        # for admin in admins:
        #     send_email(admin.email, f'Заказ {order.id}', f'{order.content}, {form.content.data}')
        send_info(
            f'{message}')
        return redirect('/')
    return render_template('make_order.html', title='Заказ', form=form)


def make_order_text(order):
    answer = ''
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == int(order.user_id)).first()
    answer += f'данные о пользователе:\n{user.tel}\n{user.email}\n{user.name}\n\n'
    answer += f'данные о заказе:\nАдрес:{order.address}\nВремя к которому доставить:{order.to_date}\nКомментарий:{order.data}\n\nТовары:\n'
    for item in order.content:
        product = db_sess.query(Products).filter(Products.id == int(item)).first()
        answer += f'\nТовар:{product.title}\nКоличество:{order.content[item]}\n'
    return answer


@app.route('/basket', methods=['GET', 'POST'])
@login_required
def user_basket():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    basket = ast.literal_eval(user.basket)
    content = basket.copy()

    for key in basket:
        db_sess = db_session.create_session()
        product = db_sess.query(Products).filter(Products.id == int(key)).first()
        if product.img:
            product.img = product.img.split(', ')
        basket[key] = [basket[key], product]
    data = []
    for key in basket:
        data.append((key, key))
    form = BasketForm(data=data)

    if form.validate_on_submit() and form.submit.data:
        session['order'] = {'content': content, 'to_order': form.content.data}
        if len(form.content.data):
            return redirect('/make_order')
        else:
            return render_template('basket.html', title='Корзина', user=user, basket=basket, form=form,
                                   message='Не выбрано ни одного товара')
    form.content.data = [key for key in basket]
    return render_template('basket.html', title='Корзина', user=user, basket=basket, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    form = ConfirmationForm()
    if form.validate_on_submit():
        # return str(check_password_hash(session.get('user').get('password'), form.code.data))
        if check_password_hash(session.get('user').get('password'), form.code.data):
            email = session.get('user').get('email')
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == email).first()
            user.confirmed = True
            db_sess.commit()
            return redirect('/login')
        else:
            return render_template('confirmation.html', title='Подтверждение', form=form, message='Неверный код')
    return render_template('confirmation.html', title='Подтверждение', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            tel=form.tel.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        password = ''
        for i in range(4):
            password += str(randint(0, 9))
        send_data = send_email(form.email.data, 'Ваш код подтверждения в Оксана.corparated', f'{password}')
        if not send_data[0]:
            return render_template('register.html', title='Регистрация', form=form,
                                   message='Возникла ошибка при отправке письма')
        password = generate_password_hash(password)
        session['user'] = {'id': user.id, 'email': form.email.data, 'password': password}
        return redirect('/confirmation')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/balloons.db")

    # port = int(os.environ.get("PORT", 5000))
    port = 5000
    app.register_blueprint(products_api.blueprint)
    app.run(host='0.0.0.0', port=port, debug=True)
    # serve(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
