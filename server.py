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
# from waitress import serve
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
from forms.products import ProductForm, ProductGroupForm
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
    return render_template('pages/index.html', products=products, view='nocube')


@app.route('/product/<int:product_group_id>/<int:product_id>', methods=['GET', 'POST'])
def show_product(product_group_id, product_id):
    return render_template('pages/show_product.html', title=propd)


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
        return render_template('pages/admin_types.html', title='Админ панель',
                               types=types, form=form)


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_user():
    if current_user.admin:
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return render_template('pages/admin_users.html', title='Админ панель',
                               users=users)


@app.route('/admin/orders', methods=['GET', 'POST'])
@login_required
def admin_orders():
    if current_user.admin: 
        db_sess = db_session.create_session()
        orders = db_sess.query(Order).all()
        return render_template('pages/admin_orders.html', title='Админ панель',
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
        return render_template('pages/admin_products.html', title='Админ панель',
                               products=products)
    else:
        return render_template('pages/no_rights.html')


@app.route('/admin/productsgroups', methods=['GET', 'POST'])
@login_required
def admin_productsgroup():
    if current_user.admin:
        db_sess = db_session.create_session()
        productgroups = db_sess.query(ProductGroup).all()
        return render_template('pages/admin_product_groups.html', title='Админ панель',
                               productgroups=productgroups)
    else:
        return render_template('pages/no_rights.html')


@app.route('/admin/add-productgroup', methods=['GET', 'POST'])
def add_productgroup():
    data = []

    db_sess = db_session.create_session()
    types = db_sess.query(Types).all()
    types_data = []
    for i in types:
        types_data.append((i.id, i.title))
    form = ProductGroupForm(types=types_data)
    if form.validate_on_submit():
        productgroup = ProductGroup()
        productgroup.title = form.title.data
        productgroup.description = form.description.data
        productgroup.type = form.type.data
        db_sess = db_session.create_session()
        db_sess.add(productgroup)
        db_sess.commit()
        return redirect('/admin/productsgroups')
    return render_template("pages/admin_add_products_group.html", data=data, form=form)


@app.route('/admin/edit-productgroup/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product_group(id):
    db_sess = db_session.create_session()
    types = db_sess.query(Types).all()
    types_data = []
    for i in types:
        types_data.append((i.id, i.title))

    db_sess = db_session.create_session()
    productgroup = db_sess.query(ProductGroup).filter(ProductGroup.id == id).first()
    if not productgroup:
        return ("Такого продукта нет")
    form = ProductGroupForm(types=types_data, type=int(productgroup.type))
    if request.method == "GET":
        if productgroup:
            form.title.data = productgroup.title
            form.description.data = productgroup.description
            form.type.data = productgroup.type
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        productgroup = db_sess.query(ProductGroup).filter(ProductGroup.id == id).first()
        if productgroup:
            productgroup.title = form.title.data
            productgroup.description = form.description.data
            productgroup.type = form.type.data
            db_sess.commit()
            return redirect('/admin/productsgroups')
        else:
            abort(404)
    db_sess = db_session.create_session()
    data = {'change': '1'}
    return render_template('pages/admin_add_products_group.html',
                           title='Редактирование Продукта',
                           form=form, data=data
                           )


@app.route('/admin/products-productgroup/<int:group_id>')
def products_in_group(group_id):
    db_sess = db_session.create_session()
    productgroup = db_sess.query(ProductGroup).filter(ProductGroup.id == group_id).first()
    if not productgroup:
        abort(404)
    for product in productgroup.products:
        product.img = product.img.split(', ')
    return render_template('pages/admin_product_in_products_group.html',
                           title=f'Продукты {productgroup.title}',
                           productgroup=productgroup
                           )


@app.route('/admin/add-product/', defaults={'sender': -1}, methods=['GET', 'POST'])
@app.route('/admin/add-product/<int:sender>', methods=['GET', 'POST'])
def add_product(sender):
    db_sess = db_session.create_session()
    product_groups = db_sess.query(ProductGroup).all()
    product_groups_data = []
    for i in product_groups:
        product_groups_data.append((i.id, i.title))
    form = ProductForm(product_groups=product_groups_data)
    if request.method == "GET" and sender != -1:
        form.product_group.data = int(sender)
    if form.validate_on_submit():
        if form.product_group.data == '-1':
            return render_template("pages/add_product.html", data={'change': '0'}, form=form, title='добавление товара',
                                   message='выберите группу товара')
        product = Products()
        product.product_group_id = form.product_group.data
        product.color = form.color.data
        product.sale = int(form.sale.data)
        product.cost = int(form.cost.data)
        product.remains = int(form.remains.data)
        db_sess = db_session.create_session()
        db_sess.add(product)
        db_sess.commit()
        if form.img.data[0].filename:
            product_id = product.id

            files_filenames = []
            for i, file in enumerate(form.img.data):
                data_filename = file.filename
                data_filename = f"{product_id}_{i}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
                file.save(os.path.join('./static/img/products', data_filename))
                files_filenames.append(data_filename)
            db_sess = db_session.create_session()
            product = db_sess.query(Products).filter(Products.id == product_id).first()
            product.img = f'{", ".join(files_filenames)}'
            db_sess.commit()
        redirect_address = '/admin/products'
        if sender != -1:
            redirect_address = f'/admin/products-productgroup/{sender}'
        return redirect(redirect_address)

    mypath = "./static/img"
    data = {'change': '0'}
    return render_template("pages/add_product.html", data=data, form=form, title='добавление товара')


@app.route('/admin/edit-product/<int:product_id>/', defaults={'sender': -1}, methods=['GET', 'POST'])
@app.route('/admin/edit-product/<int:product_id>/<int:sender>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id, sender):
    mypath = "./static/img/products"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    all_imgs = list(
        filter(lambda x: (x.endswith(".jpg") or x.endswith(".png")) and x.split('_')[0] == str(product_id), onlyfiles))

    max_img_number = 0
    if len(all_imgs):
        max_img_number = max(all_imgs, key=lambda z: int(z.split('_')[1]))
        max_img_number = int(max_img_number.split('_')[1]) + 1

    db_sess = db_session.create_session()
    groups = db_sess.query(ProductGroup).all()
    groups_data = []
    for group in groups:
        groups_data.append(tuple([group.id, group.title]))

    product = db_sess.query(Products).filter(Products.id == product_id).first()
    if not product:
        abort(404)
    if product.img:
        product.img.split(', ')
    choises = []
    if product.img:
        for elem in product.img:
            choises.append((elem, elem))
    form = ProductForm(imgs_data=all_imgs, product_groups=groups_data, must_upload=False,
                       product_group=product.product_group_id)
    if request.method == "GET":
        form.color.data = product.color
        form.product_group.data = product.product_group_id
        form.sale.data = product.sale
        form.cost.data = product.cost
        form.imgs.data = product.img
        form.remains.data = product.remains
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = db_sess.query(Products).filter(Products.id == product_id).first()
        if product:
            product.product_group_id = form.product_group.data
            product.color = form.color.data
            product.sale = form.sale.data
            product.cost = form.cost.data
            product.remains = form.remains.data
            product.img = ', '.join(form.imgs.data)
            if form.img.data[0].filename != '':

                files_filenames = []
                for i, file in enumerate(form.img.data, start=max_img_number):
                    data_filename = secure_filename(file.filename)
                    data_filename = f"{product_id}_{i}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
                    file.save(os.path.join('./static/img/products', data_filename))
                    files_filenames.append(data_filename)
                if len(product.img):
                    product.img += f', {", ".join(files_filenames)}'
                else:
                    product.img += f'{", ".join(files_filenames)}'
            db_sess.commit()
            redirect_address = '/admin/products'
            if sender != -1:
                redirect_address = f'/admin/products-productgroup/{sender}'
            return redirect(redirect_address)
            # return str(form.img.data)
        else:
            abort(404)
    db_sess = db_session.create_session()
    product = db_sess.query(Products).filter(Products.id == product_id).first()
    data = {'change': '1', 'img': product.img}
    return render_template('pages/add_product.html',
                           title='Редактирование товара',
                           form=form, data=data
                           )


@app.route('/remove_item/<string:type>/<int:id>', methods=['GET', 'POST'])
def remove_item(type, id):
    if current_user.admin:
        if type == 'products':
            db_sess = db_session.create_session()
            db_sess.query(Products).filter(Products.id == id).delete()
            db_sess.commit()
        return redirect('/admin/products')
    else:
        return render_template('pages/no_rights.html')


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
    return render_template('pages/make_order.html', title='Заказ', form=form)


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
            return render_template('pages/basket.html', title='Корзина', user=user, basket=basket, form=form,
                                   message='Не выбрано ни одного товара')
    form.content.data = [key for key in basket]
    return render_template('pages/basket.html', title='Корзина', user=user, basket=basket, form=form)


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
        return render_template('pages/login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('pages/login.html', title='Авторизация', form=form)


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
            return render_template('pages/confirmation.html', title='Подтверждение', form=form, message='Неверный код')
    return render_template('pages/confirmation.html', title='Подтверждение', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('pages/register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('pages/register.html', title='Регистрация',
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
        if user.id == 1:
            user.admin = 1
        db_sess.commit()
        password = ''
        for i in range(4):
            password += str(randint(0, 9))
        send_data = send_email(form.email.data, 'Ваш код подтверждения в Оксана.corparated', f'{password}')
        if not send_data[0]:
            return render_template('pages/register.html', title='Регистрация', form=form,
                                   message='Возникла ошибка при отправке письма')
        password = generate_password_hash(password)
        session['user'] = {'id': user.id, 'email': form.email.data, 'password': password}
        return redirect('/confirmation')
    return render_template('pages/register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/balloons.db")

    # port = int(os.environ.get("PORT", 5000))
    port = 5000
    app.register_blueprint(products_api.blueprint)
    app.run(host='0.0.0.0', port=port, debug=True)
    # serve(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
