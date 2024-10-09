import ast
import json
import os
from datetime import datetime
from os import listdir
from os.path import isfile, join
from random import randint

from flask import Flask
from flask import render_template, redirect, request, abort, jsonify
from flask import session
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)

# from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import products_api
from bot import send_info
from data import db_session
from data.banners import Banners
from data.category import Category
from data.comments import Comments
from data.orders import Order
from data.products import Products
from data.products_group import ProductGroup
from data.types import Types
from data.users import User
from email_sender import send_email
from forms.orders import BasketForm, MakeOrder
from forms.products import ProductForm, ProductGroupForm, SearchForm, CommentsForm
from forms.types import TypeForm, CategoryForm, BannerForm
from forms.user import RegisterForm, LoginForm, ConfirmationForm

ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


UPLOAD_FOLDER = "./static/img/upload"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def undefiend(e):
    # db_sess = db_session.create_session()
    # category = db_sess.query(Category).all()
    # product = db_sess.query(Products).filter(Products.id == 9).first()
    # product.category = category
    # db_sess.commit()
    return "no fiend" ""


@app.errorhandler(401)
def unauthorized(e):
    return redirect("/login")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).filter(User.id == user_id).first()


@app.route("/href_safer", methods=["POST"])
def href_safer():
    if request.method == "POST":
        try:
            data = request.json
            if "href" in data:
                session["href"] = data.get("href")
                print(session["href"])
                return jsonify({"message": "Success!", "value": data.get("href")}), 200
            else:
                raise KeyError("Value key not found")
        except (KeyError, json.JSONDecodeError) as e:
            return jsonify({"error": "Invalid data format"}), 400
        except Exception as e:
            return jsonify({"error": "Invalid data format"}), 400


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
def index_get():
    db_sess = db_session.create_session()
    types = db_sess.query(Types).all()
    categories = db_sess.query(Category).all()
    banners = db_sess.query(Banners).filter(Banners.active == True).all()
    db_sess.close()
    return render_template(
        "pages/index.html",
        types=types,
        categories=categories,
        banners=banners,
        view="nocube",
    )


@app.route("/", methods=["POST"])
@app.route("/index", methods=["POST"])
def index_post():
    text = request.form.get("text")
    return redirect(f"/search?text={text}")


@app.route("/banner/<int:banner_id>")
def banner_get(banner_id):
    with db_session.create_session() as db_sess:
        banner = db_sess.query(Banners).filter(Banners.id == banner_id).first()
        return render_template("pages/banners.html", banner=banner)


@app.route("/search", methods=["GET", "POST"])
def search_get():
    with db_session.create_session() as db_sess:
        # db_sess = db_session.create_session()
        # types_db = db_sess.query(Types).all()
        # types_data = [(i.id, i.title) for i in types_db]
        categories_db = db_sess.query(Category).all()
        categories_data = [(i.id, i.title) for i in categories_db]
        form = SearchForm(categories_data=categories_data)
        if form.validate_on_submit():
            text = request.form.get("text", default="", type=str)
            min_cost = form.min_cost.data
            max_cost = form.max_cost.data
            category = form.categories.data
            # types = ', '.join([str(i) for i in form.types.data]) or -1
            return redirect(
                f"/search?text={text}&min_cost={min_cost}&max_cost={max_cost}&category={category}#1"
            )
        elif request.method == "GET":
            text = request.args.get("text", default="", type=str)
            min_cost = request.args.get("min_cost", default=0, type=int)
            max_cost = request.args.get("max_cost", type=int)
            category = request.args.get("category", type=int, default=-1)
            # types_post = [int(i) for i in request.args.get("types", default='-1', type=str).split(', ')]
            # # настройка формы
            # if -1 in types_post:
            #     types_post = [i[0] for i in form.types.choices]
            # form.types.data = types_post
            form.min_cost.data = min_cost
            form.max_cost.data = max_cost
            form.categories.data = category

            products = []
            products_color = []
            # if min_cost == 0 and max_cost == -1
            if text:
                for word in text.split():
                    products.append(
                        db_sess.query(Products)
                        .join(Products.product_group)
                        .filter(
                            (
                                Products.product_group.property.mapper.class_.title.like(
                                    f"%{word}%"
                                )
                            )
                            | (
                                Products.product_group.property.mapper.class_.description.like(
                                    f"%{word}%"
                                )
                            )
                        )
                        # .filter(Products.product_group.property.mapper.class_.type.in_(types_post))
                    )
                    # Category.id.in_(form.categories.data)

                    products_color.append(
                        db_sess.query(Products)
                        .join(Products.product_group)
                        .filter(Products.color.like(f"%{word}%"))
                    )
                turn = products + products_color
            else:
                turn = [db_sess.query(Products).join(Products.product_group)]
            #
            if category != -1:
                for i, item in enumerate(turn):
                    # .filter(ZKUser.groups.any(ZKGroup.id.in_([1, 2, 3])))
                    turn[i] = item.filter(
                        Products.category.any(
                            Category.id.in_(
                                [
                                    category,
                                ]
                            )
                        )
                    )
            if max_cost:
                # to_show = sorted(filter(lambda x: min_cost <= x.cost <= max_cost, set(turn)), key=lambda z: turn.index(z))
                for i, item in enumerate(turn):
                    turn[i] = item.filter(Products.cost - Products.sale <= max_cost)
            to_show = []
            for i, item in enumerate(turn):
                to_show.extend(item.filter(Products.cost >= min_cost).all())
            show_parts = {}
            for product in to_show:
                type_title = product.product_group.type_relation.title
                if type_title not in show_parts:
                    show_parts[type_title] = []
                show_parts[type_title].append(product)
            types_db = db_sess.query(Types).all()
            return render_template(
                "pages/search.html",
                title="product",
                products=to_show,
                text=text,
                min_cost=min_cost,
                max_cost=max_cost or "",
                types=types_db,
                form=form,
                show_parts=show_parts,
            )
        elif request.method == "POST":
            text = request.form.get("text", default="", type=str)
            min_cost = request.args.get("min_cost", default=0, type=int)
            max_cost = request.args.get("max_cost", type=int)
            category = request.args.get("category", type=int, default=-1)

            return redirect(
                f"/search?text={text}&min_cost={min_cost}&max_cost={max_cost}&category={category}#1"
            )


@app.route(
    "/show_product/<int:product_group_id>/<int:product_id>", methods=["GET", "POST"]
)
def show_product(product_group_id, product_id):
    with db_session.create_session() as db_sess:
        product_group = (
            db_sess.query(ProductGroup)
            .filter(ProductGroup.id == product_group_id)
            .first()
        )
        product = db_sess.query(Products).filter(Products.id == product_id).first()
        href = session.get("href") or "/search"
        print(href)
        return render_template(
            "pages/show_product.html",
            title="product",
            product=product,
            product_group=product_group,
            href=href,
        )


@app.route(
    "/comment_product/<int:product_group_id>/<int:product_id>", methods=["GET", "POST"]
)
@login_required
def comment_product(product_group_id, product_id):
    with db_session.create_session() as db_sess:
        form = CommentsForm()
        if request.method == "GET":
            comment = (
                db_sess.query(Comments)
                .filter(
                    Comments.product_group_id == product_group_id,
                    Comments.user_id == current_user.id,
                )
                .first()
            )
            if comment:
                form.plus.data = comment.plus
                form.minus.data = comment.minus
                form.content.data = comment.content
                form.mark.data = comment.mark
        elif form.validate_on_submit():
            comment = (
                db_sess.query(Comments)
                .filter(
                    Comments.product_group_id == product_group_id,
                    Comments.user_id == current_user.id,
                )
                .first()
            )
            new = False
            if not comment:
                comment = Comments()
                new = True
            comment.plus = form.plus.data
            comment.minus = form.minus.data
            comment.content = form.content.data
            comment.mark = form.mark.data
            comment.product_group_id = int(product_group_id)
            comment.user_id = int(current_user.id)
            if new:
                db_sess.add(comment)
            db_sess.commit()
            return redirect(f"/show_product/{product_group_id}/{product_id}")
        return render_template(
            "pages/comment_form.html", title="Комментарий", form=form
        )


@app.route("/admin/categories", methods=["GET", "POST"])
@login_required
def admin_categories():
    if not current_user.admin:
        return render_template("pages/no_rights.html")
    with db_session.create_session() as db_sess:
        filenames = [""]
        form = CategoryForm()
        categories = db_sess.query(Category).all()

        if form.validate_on_submit():
            # добавление продукта
            categories = Category()
            categories.title = form.title.data
            form.title.data = ""
            db_sess.add(categories)
            db_sess.commit()
            file = form.img.data
            data_filename = secure_filename(file.filename)
            data_filename = f"{categories.id}_{0}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
            file.save(os.path.join("./static/img/categories", data_filename))
            categories.img = data_filename
            db_sess.commit()
            return redirect("/admin/categories")
        if request.method == "POST":
            for id in request.form:
                type = db_sess.query(Types).filter(Types.id == id).first()
                type.title = request.form[id]
                db_sess.commit()
                # request.form[id] = ''
            return redirect("/admin/types")
        return render_template(
            "pages/admin_categories.html",
            title="Админ панель",
            categories=categories,
            form=form,
        )


@app.route("/admin/banners", methods=["GET", "POST"])
@login_required
def admin_banners():
    if not current_user.admin:
        return render_template("pages/no_rights.html")
    with db_session.create_session() as db_sess:
        banners = db_sess.query(Banners).all()
        return render_template(
            "pages/admin_banners.html", title="Админ панель", banners=banners
        )


@app.route("/admin/types", methods=["GET", "POST"])
@login_required
def admin_types():
    if not current_user.admin:
        return render_template("pages/no_rights.html")

    filenames = [""]
    form = TypeForm()
    with db_session.create_session() as db_sess:
        types = db_sess.query(Types).all()
        if form.validate_on_submit():
            # добавление продукта
            type = Types()
            type.title = form.title.data
            form.title.data = ""
            db_sess.add(type)
            db_sess.commit()
            return redirect("/admin/types")
        if request.method == "POST":
            for id in request.form:
                type = db_sess.query(Types).filter(Types.id == id).first()
                type.title = request.form[id]
                db_sess.commit()
                # request.form[id] = ''
            return redirect("/admin/types")
        return render_template(
            "pages/admin_types.html", title="Админ панель", types=types, form=form
        )


@app.route("/admin/users", methods=["GET", "POST"])
@login_required
def admin_user():
    if not current_user.admin:
        return render_template("pages/no_rights.html")
    with db_session.create_session() as db_sess:
        users = db_sess.query(User).all()
        return render_template(
            "pages/admin_users.html", title="Админ панель", users=users
        )


@app.route("/admin/orders", methods=["GET", "POST"])
@login_required
def admin_orders():
    if not current_user.admin:
        return render_template("pages/no_rights.html")
    with db_session.create_session() as db_sess:
        orders = db_sess.query(Order).all()
        return render_template(
            "pages/admin_orders.html", title="Админ панель", orders=orders
        )


@app.route("/admin/products", methods=["GET", "POST"])
@login_required
def admin_products():
    if not current_user.admin:
        return render_template("pages/no_rights.html")
    with db_session.create_session() as db_sess:
        products = db_sess.query(Products).all()
        return render_template(
            "pages/admin_products.html", title="Админ панель", products=products
        )


@app.route("/admin/productsgroups", methods=["GET", "POST"])
@login_required
def admin_productsgroup():
    if not current_user.admin:
        return render_template("pages/no_rights.html")

    with db_session.create_session() as db_sess:
        productgroups = db_sess.query(ProductGroup).all()
        return render_template(
            "pages/admin_product_groups.html",
            title="Админ панель",
            productgroups=productgroups,
        )


@app.route("/admin/edit-category/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    if not current_user.admin:
        return render_template("pages/no_rights.html")

    mypath = "./static/img/categories"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    all_imgs = list(
        filter(
            lambda x: (x.endswith(".jpg") or x.endswith(".png"))
            and x.split("_")[0] == str(category_id),
            onlyfiles,
        )
    )

    with db_session.create_session() as db_sess:
        products = db_sess.query(Products).all()
        products_data = []
        for product in products:
            products_data.append(
                (product.id, product.product_group.title + " " + product.color)
            )
        category = db_sess.query(Category).filter(Category.id == category_id).first()
        if not category:
            return "Такогой категории нет"
        form = CategoryForm()
        if request.method == "GET":
            if category:
                form.title.data = category.title
            else:
                abort(404)
        if form.validate_on_submit():
            category = (
                db_sess.query(Category).filter(Category.id == category_id).first()
            )
            if category:
                category.title = form.title.data
                db_sess.commit()

                if form.img.data.filename != "":
                    if len(all_imgs):
                        os.remove(os.path.join("./static/img/categories", all_imgs[0]))

                    file = form.img.data
                    data_filename = secure_filename(file.filename)
                    data_filename = f"{category_id}_{0}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
                    file.save(os.path.join("./static/img/categories", data_filename))
                    category.img = data_filename
                    db_sess.commit()

                db_sess.commit()
                return redirect("/admin/categories")
            else:
                abort(404)
        return render_template(
            "pages/admin_edit_category.html",
            title="Редактирование Категории",
            form=form,
        )


@app.route("/admin/add-banner", methods=["GET", "POST"])
@login_required
def add_banner():
    if not current_user.admin:
        return render_template("pages/no_rights.html")
    with db_session.create_session() as db_sess:
        products = db_sess.query(Products).all()
        products_data = []
        for product in products:
            products_data.append(
                (product.id, product.product_group.title + " " + product.color)
            )
        form = BannerForm(products_data=products_data)
        if form.validate_on_submit():
            banner = Banners()
            banner.title = form.title.data
            banner.active = form.active.data
            banner.products.extend(
                db_sess.query(Products).filter(Products.id.in_(form.products.data))
            )
            db_sess.add(banner)
            db_sess.commit()
            file = form.img.data
            data_filename = secure_filename(file.filename)
            data_filename = f"{banner.id}_{0}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
            file.save(os.path.join("./static/img/banners", data_filename))
            banner.img = data_filename
            db_sess.commit()
            return redirect("/admin/banners")
        return render_template("pages/admin_add_banner.html", form=form)


@app.route("/admin/edit-banner/<int:banner_id>", methods=["GET", "POST"])
@login_required
def edit_banner(banner_id):
    if not current_user.admin:
        return render_template("pages/no_rights.html")
    mypath = "./static/img/banners"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    all_imgs = list(
        filter(
            lambda x: (x.endswith(".jpg") or x.endswith(".png"))
            and x.split("_")[0] == str(banner_id),
            onlyfiles,
        )
    )

    with db_session.create_session() as db_sess:
        products = db_sess.query(Products).all()
        products_data = []
        for product in products:
            products_data.append(
                (product.id, product.product_group.title + " " + product.color)
            )
        banner = db_sess.query(Banners).filter(Banners.id == banner_id).first()
        if not banner:
            return "Такого баннера нет"
        form = BannerForm(products_data=products_data, products=products_data)
        if request.method == "GET":
            if banner:
                form.title.data = banner.title
                form.active.data = banner.active
                form.products.data = banner.get_products_id()
            else:
                abort(404)
        if form.validate_on_submit():
            banner = db_sess.query(Banners).filter(Banners.id == banner_id).first()
            if banner:
                banner.title = form.title.data
                banner.active = form.active.data
                banner.products = (
                    db_sess.query(Products)
                    .filter(Products.id.in_(form.products.data))
                    .all()
                )
                if form.img.data.filename != "":
                    if len(all_imgs):
                        os.remove(os.path.join("./static/img/banners", all_imgs[0]))

                    file = form.img.data
                    data_filename = secure_filename(file.filename)
                    data_filename = f"{banner_id}_{0}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
                    file.save(os.path.join("./static/img/banners", data_filename))
                    banner.img = data_filename
                    db_sess.commit()

                db_sess.commit()
                return redirect("/admin/banners")
            else:
                abort(404)
        return render_template(
            "pages/admin_add_banner.html", title="Редактирование Продукта", form=form
        )


@app.route("/admin/add-productgroup", methods=["GET", "POST"])
@login_required
def add_productgroup():
    if not current_user.admin:
        return render_template("pages/no_rights.html")

    data = []
    with db_session.create_session() as db_sess:
        types = db_sess.query(Types).all()
        types_data = []
        for type in types:
            types_data.append((type.id, type.title))
        form = ProductGroupForm(types=types_data)
        if form.validate_on_submit():
            productgroup = ProductGroup()
            productgroup.title = form.title.data
            productgroup.description = form.description.data
            productgroup.type = form.type.data
            db_sess.add(productgroup)
            db_sess.commit()
            return redirect("/admin/productsgroups")
        return render_template(
            "pages/admin_add_products_group.html", data=data, form=form
        )


@app.route("/admin/edit-productgroup/<int:id>", methods=["GET", "POST"])
@login_required
def edit_product_group(id):
    if not current_user.admin:
        return render_template("pages/no_rights.html")

    with db_session.create_session() as db_sess:
        types = db_sess.query(Types).all()
        types_data = []
        for i in types:
            types_data.append((i.id, i.title))

        productgroup = db_sess.query(ProductGroup).filter(ProductGroup.id == id).first()
        if not productgroup:
            return "Такого продукта нет"
        form = ProductGroupForm(types=types_data, type=int(productgroup.type))
        if request.method == "GET":
            if productgroup:
                form.title.data = productgroup.title
                form.description.data = productgroup.description
                form.type.data = productgroup.type
            else:
                abort(404)
        if form.validate_on_submit():
            productgroup = (
                db_sess.query(ProductGroup).filter(ProductGroup.id == id).first()
            )
            if productgroup:
                productgroup.title = form.title.data
                productgroup.description = form.description.data
                productgroup.type = form.type.data
                db_sess.commit()
                return redirect("/admin/productsgroups")
            else:
                abort(404)
        data = {"change": "1"}
        return render_template(
            "pages/admin_add_products_group.html",
            title="Редактирование Продукта",
            form=form,
            data=data,
        )


@app.route("/admin/products-productgroup/<int:group_id>")
@login_required
def products_in_group(group_id):
    if not current_user.admin:
        return render_template("pages/no_rights.html")

    with db_session.create_session() as db_sess:
        productgroup = (
            db_sess.query(ProductGroup).filter(ProductGroup.id == group_id).first()
        )
        if not productgroup:
            abort(404)
        return render_template(
            "pages/admin_product_in_products_group.html",
            title=f"Продукты {productgroup.title}",
            productgroup=productgroup,
        )


@app.route("/admin/add-product/", defaults={"sender": -1}, methods=["GET", "POST"])
@app.route("/admin/add-product/<int:sender>", methods=["GET", "POST"])
@login_required
def add_product(sender):
    if not current_user.admin:
        return render_template("pages/no_rights.html")

    with db_session.create_session() as db_sess:
        product_groups = db_sess.query(ProductGroup).all()
        product_groups_data = []
        for group in product_groups:
            product_groups_data.append((group.id, group.title))
        categories = db_sess.query(Category).all()
        categories_data = []
        for category in categories:
            categories_data.append((category.id, category.title))
        form = ProductForm(
            product_groups=product_groups_data, categories=categories_data
        )
        if request.method == "GET" and sender != -1:
            form.product_group.data = int(sender)
        if form.validate_on_submit():
            if form.product_group.data == -1:
                return render_template(
                    "pages/admin_add_product.html",
                    data={"change": "0"},
                    form=form,
                    title="добавление товара",
                    message="выберите группу товара",
                )
            product = Products()
            product.product_group_id = form.product_group.data
            product.color = form.color.data
            product.sale = int(form.sale.data)
            product.cost = int(form.cost.data)
            product.remains = int(form.remains.data)
            product.category.extend(
                db_sess.query(Category).filter(Category.id.in_(form.categories.data))
            )
            db_sess.add(product)
            db_sess.commit()
            if form.img.data[0].filename:
                product_id = product.id

                files_filenames = []
                for i, file in enumerate(form.img.data):
                    data_filename = file.filename
                    data_filename = f"{product_id}_{i}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
                    file.save(os.path.join("./static/img/products", data_filename))
                    files_filenames.append(data_filename)
                product = (
                    db_sess.query(Products).filter(Products.id == product_id).first()
                )
                product.img = f'{", ".join(files_filenames)}'
                db_sess.commit()
            redirect_address = "/admin/products"
            if sender != -1:
                redirect_address = f"/admin/products-productgroup/{sender}"
            return redirect(redirect_address)

        mypath = "./static/img"
        data = {"change": "0"}
        return render_template(
            "pages/admin_add_product.html",
            data=data,
            form=form,
            title="добавление товара",
        )


@app.route(
    "/admin/edit-product/<int:product_id>/",
    defaults={"sender": -1},
    methods=["GET", "POST"],
)
@app.route("/admin/edit-product/<int:product_id>/<int:sender>", methods=["GET", "POST"])
@login_required
def edit_product(product_id, sender):
    if not current_user.admin:
        return render_template("pages/no_rights.html")
    mypath = "./static/img/products"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    all_imgs = list(
        filter(
            lambda x: (x.endswith(".jpg") or x.endswith(".png"))
            and x.split("_")[0] == str(product_id),
            onlyfiles,
        )
    )

    max_img_number = 0
    if len(all_imgs):
        max_img_number = max(all_imgs, key=lambda z: int(z.split("_")[1]))
        max_img_number = int(max_img_number.split("_")[1]) + 1

    with db_session.create_session() as db_sess:
        groups = db_sess.query(ProductGroup).all()
        groups_data = []
        for group in groups:
            groups_data.append(tuple([group.id, group.title]))

        product = db_sess.query(Products).filter(Products.id == product_id).first()
        if not product:
            abort(404)
        categories = db_sess.query(Category).all()
        categories_data = []
        for category in categories:
            categories_data.append((category.id, category.title))
        form = ProductForm(
            imgs_data=all_imgs,
            product_groups=groups_data,
            must_upload=False,
            product_group=product.product_group_id,
            categories=categories_data,
        )
        if request.method == "GET":
            form.color.data = product.color
            form.product_group.data = product.product_group_id
            form.sale.data = product.sale
            form.cost.data = product.cost
            form.imgs.data = product.get_img()
            form.remains.data = product.remains
            form.categories.data = product.get_categories_id()
        if form.validate_on_submit():
            product = db_sess.query(Products).filter(Products.id == product_id).first()
            if product:
                product.product_group_id = form.product_group.data
                product.color = form.color.data
                product.sale = form.sale.data
                product.cost = form.cost.data
                product.remains = form.remains.data
                product.img = ", ".join(form.imgs.data)
                product.category = (
                    db_sess.query(Category)
                    .filter(Category.id.in_(form.categories.data))
                    .all()
                )
                if form.img.data[0].filename != "":

                    files_filenames = []
                    for i, file in enumerate(form.img.data, start=max_img_number):
                        data_filename = secure_filename(file.filename)
                        data_filename = f"{product_id}_{i}_{datetime.now().date()}.{data_filename.split('.')[-1]}"
                        file.save(os.path.join("./static/img/products", data_filename))
                        files_filenames.append(data_filename)
                    if len(product.img):
                        product.img += f', {", ".join(files_filenames)}'
                    else:
                        product.img += f'{", ".join(files_filenames)}'
                db_sess.commit()
                redirect_address = "/admin/products"
                if sender != -1:
                    redirect_address = f"/admin/products-productgroup/{sender}"
                return redirect(redirect_address)
                # return str(form.img.data)
            else:
                abort(404)
        product = db_sess.query(Products).filter(Products.id == product_id).first()
        data = {"change": "1", "img": product.img}
        return render_template(
            "pages/admin_add_product.html",
            title="Редактирование товара",
            form=form,
            data=data,
        )


@app.route(
    "/remove_item/<string:type>/<int:id>/<string:sender>", methods=["GET", "POST"]
)
@login_required
def remove_item(type, id, sender):
    if not current_user.admin:
        return render_template("pages/no_rights.html")
    with db_session.create_session() as db_sess:
        if type == "products":
            product = db_sess.query(Products).filter(Products.id == id).first()
            product.category = []
            db_sess.commit()
            db_sess.query(Products).filter(Products.id == id).delete()
            db_sess.commit()

            mypath = "./static/img/products"
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            product_imgs = list(
                filter(
                    lambda x: (x.endswith(".jpg") or x.endswith(".png"))
                    and x.split("_")[0] == str(id),
                    onlyfiles,
                )
            )
            for img_name in product_imgs:
                os.remove(f"{mypath}/{img_name}")
            redirect_address = "/admin/products"
            if sender != "-1":
                redirect_address = f"/admin/products-productgroup/{sender}"
            return redirect(redirect_address)
        elif type == "productgroup":
            product_group = (
                db_sess.query(ProductGroup).filter(ProductGroup.id == id).first()
            )
            for color in product_group.products:
                product = (
                    db_sess.query(Products).filter(Products.id == color.id).first()
                )
                product.category = []
                db_sess.commit()
                db_sess.query(Products).filter(Products.id == color.id).delete()
                mypath = "./static/img/products"
                onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
                product_imgs = list(
                    filter(
                        lambda x: (x.endswith(".jpg") or x.endswith(".png"))
                        and x.split("_")[0] == str(color.id),
                        onlyfiles,
                    )
                )
                for img_name in product_imgs:
                    os.remove(f"{mypath}/{img_name}")
            db_sess.query(ProductGroup).filter(ProductGroup.id == id).delete()
            db_sess.commit()
            return redirect("/admin/productsgroups")
        elif type == "banners":
            banner = db_sess.query(Banners).filter(Banners.id == id).first()
            banner.products = []
            db_sess.commit()
            db_sess.query(Banners).filter(Banners.id == id).delete()
            db_sess.commit()

            mypath = "./static/img/banners"
            onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
            banners_img = list(
                filter(
                    lambda x: (x.endswith(".jpg") or x.endswith(".png"))
                    and x.split("_")[0] == str(id),
                    onlyfiles,
                )
            )
            for img_name in banners_img:
                os.remove(f"{mypath}/{img_name}")
            return redirect("/admin/banners")


@app.route("/make_order", methods=["GET", "POST"])
@login_required
def user_make_order():
    content = {}
    first_content = session.get("order").get("content")
    to_order = session.get("order").get("to_order")
    for i in to_order:
        content[i] = first_content[i]
    form = MakeOrder()
    db_sess = db_session.create_session()
    products = (
        db_sess.query(Products).filter(Products.id.in_([int(i) for i in content])).all())
    cost = sum([(i.cost - i.sale) * content[str(i.id)] for i in products])
    content = {int(i): content[i] for i in content}
    if form.validate_on_submit():
        date = datetime.fromisoformat(str(form.date.data) + "T" + str(form.time.data))
        # time = datetime.strptime(str(form.time.data))
        db_sess = db_session.create_session()
        order = Order(
            content=str(content),
            user_id=current_user.id,
            to_date=date,
            data=form.description.data,
            address=form.address.data,
            how_pay=form.how_pay.data,
            cost=cost,
        )
        db_sess.add(order)
        db_sess.commit()
        message = make_order_text(order)

        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.basket = ast.literal_eval(user.basket)
        for product_id in content:
            if str(product_id) in user.basket:
                del user.basket[str(product_id)]
        user.basket = str(user.basket)
        db_sess.commit()

        db_sess = db_session.create_session()
        admins = db_sess.query(User).filter(User.admin == True).all()
        for admin in admins:
            send_email(admin.email, f"Заказ {message[0]}", f"{message[1]}")
        send_info(f"{message[2]}")
        return redirect("/")
    return render_template(
        "pages/make_order.html",
        title="Заказ",
        form=form,
        products=products,
        cost=cost,
        content=content,
    )


def make_order_text(order):
    answer = ""
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == int(order.user_id)).first()
    answer += (
        f"данные о пользователе:<br>{user.tel}<br>{user.email}<br>{user.name}<br><br>"
    )
    answer += f"данные о заказе:<br>Стоимость:{order.cost}<br>Адрес:{order.address}<br>Время к которому доставить:{order.to_date}<br>Комментарий:<br><code>{order.data}</code><br><br>Товары:<br>"
    for item in ast.literal_eval(order.content):
        product = db_sess.query(Products).filter(Products.id == int(item)).first()
        answer += f"\nТовар: {product.product_group.title} {product.color}\nКоличество: {ast.literal_eval(order.content)[item]}\n"
    return order.id, answer, answer.replace("<br>", "\n")


def validate(value):
    return value


@app.route("/basket", methods=["GET", "POST"])
@login_required
def user_basket():
    if request.method == "POST":
        try:
            data = request.json
            if "href" in data:
                session["basket_href"] = data.get("href")
                return jsonify({"message": "Success!", "value": data.get("href")}), 200
            else:
                raise KeyError("Value key not found")
        except (KeyError, json.JSONDecodeError) as e:
            return jsonify({"error": "Invalid data format"}), 400
        except Exception as e:
            ...
    href = session.get("basket_href") or "/index"

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    basket = ast.literal_eval(user.basket)

    content = basket.copy()

    for key in basket:
        product = db_sess.query(Products).filter(Products.id == int(key)).first()
        basket[key] = [basket[key], product]
    data = []
    for key in basket:
        data.append((key, key))
    form = BasketForm(data=data)

    if form.validate_on_submit() and form.submit.data:
        session["order"] = {"content": content, "to_order": form.content.data}
        if len(form.content.data):
            return redirect("/make_order")
        else:
            return render_template(
                "pages/basket.html",
                title="Корзина",
                user=user,
                basket=basket,
                form=form,
                message="Не выбрано ни одного товара",
                hrefBack=href,
            )
    form.content.data = [key for key in basket]
    return render_template(
        "pages/basket.html",
        title="Корзина",
        user=user,
        basket=basket,
        form=form,
        hrefBack=href,
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    href_redirect = session.get("href") or "/"
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect(href_redirect)
        return render_template(
            "pages/login.html", message="Неправильный логин или пароль", form=form
        )
    return render_template("pages/login.html", title="Авторизация", form=form)


@app.route("/confirmation", methods=["GET", "POST"])
def confirmation():
    form = ConfirmationForm()
    if form.validate_on_submit():
        # return str(check_password_hash(session.get('user').get('password'), form.code.data))
        if check_password_hash(session.get("user").get("password"), form.code.data):
            email = session.get("user").get("email")
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.email == email).first()
            user.confirmed = True
            db_sess.commit()
            return redirect("/login")
        else:
            return render_template(
                "pages/confirmation.html",
                title="Подтверждение",
                form=form,
                message="Неверный код",
            )
    return render_template("pages/confirmation.html", title="Подтверждение", form=form)


@app.route("/register", methods=["GET", "POST"])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template(
                "pages/register.html",
                title="Регистрация",
                form=form,
                message="Пароли не совпадают",
            )
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "pages/register.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = User(name=form.name.data, email=form.email.data, tel=form.tel.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        if user.id == 1:
            user.admin = 1
        db_sess.commit()
        password = ""
        for i in range(4):
            password += str(randint(0, 9))
        send_data = send_email(
            form.email.data, "Ваш код подтверждения в Оксана.corparated", f"{password}"
        )
        if not send_data[0]:
            return render_template(
                "pages/register.html",
                title="Регистрация",
                form=form,
                message="Возникла ошибка при отправке письма",
            )
        password = generate_password_hash(password)
        session["user"] = {
            "id": user.id,
            "email": form.email.data,
            "password": password,
        }
        return redirect("/confirmation")
    return render_template("pages/register.html", title="Регистрация", form=form)


def main():
    db_session.global_init("db/balloons.db")

    # port = int(os.environ.get("PORT", 5000))
    port = 5000
    app.register_blueprint(products_api.blueprint)
    app.run(host="0.0.0.0", port=port, debug=True)
    # serve(app, host='0.0.0.0', port=port)


if __name__ == "__main__":
    main()
