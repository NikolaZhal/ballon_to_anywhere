import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Products(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    color = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("types.id"))
    sale = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    special_offer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cost = sqlalchemy.Column(sqlalchemy.Integer)
    remains = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    img = sqlalchemy.Column(sqlalchemy.String, default='none.jpg')
    type_relation = orm.relationship('Types')
    product_group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("product_group.id"))
    product_group = orm.relationship('ProductsGroup')

    def __repr__(self):
        return f'<products> {self.id} {self.title}'

    def add_during(self, data):
        self.during = data
