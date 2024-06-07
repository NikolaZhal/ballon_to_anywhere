from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired


class TypeForm(FlaskForm):
    title = StringField('Название типа', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class CategoryForm(FlaskForm):
    title = StringField('Название категории', validators=[DataRequired()])
    img = FileField(validators=[DataRequired()])
    submit = SubmitField('Добавить')
