import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

Products_to_Category_table = sqlalchemy.Table(
    'products_to_category',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('products', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column('category', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('category.id'))
)


class Category(SqlAlchemyBase):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # products = orm.relationship("Products",
    #                             secondary="products_to_category",
    #                             backref="category")
