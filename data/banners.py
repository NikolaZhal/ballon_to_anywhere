import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

Products_to_Banners_table = sqlalchemy.Table(
    "products_to_banners",
    SqlAlchemyBase.metadata,
    sqlalchemy.Column(
        "products", sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id")
    ),
    sqlalchemy.Column(
        "banners", sqlalchemy.Integer, sqlalchemy.ForeignKey("banners.id")
    ),
)


class Banners(SqlAlchemyBase):
    __tablename__ = "banners"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    active = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    img = sqlalchemy.Column(sqlalchemy.String, default="0_0_0_none.jpg")
    products = orm.relationship(
        "Products", secondary="products_to_banners", backref="banners"
    )

    def get_products_id(self):
        return str([i.id for i in self.products])

    def __repr__(self):
        return f"<banners {self.id}, {self.title}>"
