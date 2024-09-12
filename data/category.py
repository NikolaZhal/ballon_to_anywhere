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
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    img = sqlalchemy.Column(sqlalchemy.String, default='0_0_0_none.jpg')

    def get_products_id(self):
        return str([i.id for i in self.products])
    def __repr__(self):
        return f'<category {self.id}, {self.title}>'
