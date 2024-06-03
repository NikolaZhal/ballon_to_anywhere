import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    plus = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    minus = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    mark = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    product_group_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("product_group.id"))
    product_group = orm.relationship('ProductGroup')

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    def show_data(self):
        return f'{self.id}\n{self.content}\tОценка:{self.mark}\t{self.plus}\n{self.minus}\n{self.product_group_id}'
    def __repr__(self):
        return f'<comments> {self.id} {self.content}'
