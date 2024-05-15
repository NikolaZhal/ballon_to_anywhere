import datetime

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Types(SqlAlchemyBase):
    __tablename__ = 'types'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    products = orm.relationship("ProductGroup", back_populates='type_relation')

    def __repr__(self):
        return f'<type> {self.id} {self.title}'
