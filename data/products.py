import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Products(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    # title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    color = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    sale = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer)
    remains = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    img = sqlalchemy.Column(sqlalchemy.String, default='0_0_0_none.jpg')
    product_group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("product_group.id"))
    product_group = orm.relationship('ProductGroup')
    category = orm.relationship("Category",
                                secondary="products_to_category",
                                backref="products")

    def get_img(self):
        return self.img.split(', ')

    def get_price(self):
        if self.sale == 0:
            return str(self.cost)
        return f'<del>{self.cost}</del> {self.cost - self.sale}'

    def get_categories_id(self):
        return [i.id for i in self.category]

    def __repr__(self):
        return f'<products> {self.id} {self.color}'
