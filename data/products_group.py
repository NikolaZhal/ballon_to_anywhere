import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class ProductGroup(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'product_group'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("types.id"))
    type_relation = orm.relationship('Types')
    products = orm.relationship("Products", back_populates='product_group')
    comments = orm.relationship("Comments", back_populates='product_group')

    def get_average_mark(self):
        average = round(sum([comment.mark for comment in self.comments]) / len(self.comments), 2) if len(
            self.comments) else 'no comments later'
        return f'{average}<span style="color: yellow;">★</span> {len(self.comments)} оценок'

    def __repr__(self):
        return f'<products_group {self.id} {self.title}>'
