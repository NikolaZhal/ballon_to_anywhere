from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, MultipleFileField, widgets, SelectMultipleField, \
    TextAreaField, IntegerField, RadioField, FileField, BooleanField
from wtforms.validators import DataRequired
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class TypeForm(FlaskForm):
    title = StringField('Название типа', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class CategoryForm(FlaskForm):
    title = StringField('Название категории', validators=[DataRequired()])
    img = FileField()
    submit = SubmitField('Добавить')


class BannerForm(FlaskForm):
    title = StringField('Название баннера', validators=[DataRequired()])
    img = FileField()
    active = BooleanField("Активен")
    products = MultiCheckboxField('Продукты', choices=[])
    submit = SubmitField('Подтвердить')

    def __init__(self, *args, products_data=[(-1, 'Нет изображений')], **kwargs):
        super().__init__(*args, **kwargs)
        self.products.choices = products_data
