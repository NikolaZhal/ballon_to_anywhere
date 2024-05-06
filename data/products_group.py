import datetime

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class ProductGroup(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'product_group'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    products_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    products = orm.relationship("Products", back_populates='product_group')

    def __repr__(self):
        return f'<products_group> {self.id} {self.title}'