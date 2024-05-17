from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, MultipleFileField, widgets, SelectMultipleField, \
    TextAreaField
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class ProductGroupForm(FlaskForm):
    title = StringField('Название продукта (цветовой группы)', validators=[DataRequired()])
    description = TextAreaField('Описание продукта (цветовой группы)', validators=[DataRequired()])
    type = SelectField('Тип продукта (цветовой группы)', coerce=int, choices=[(-1, 'Если необходимо создайте тип')])
    submit = SubmitField('Создать продукта')

    def __init__(self, *args, types=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.type.choices = types

class ProductForm(FlaskForm):
    color = StringField('Цвет продукта (единицы цветовой группы)', validators=[DataRequired()])
    product_group = SelectField('Наименование группы товара',coerce=int , choices=[(-1, 'Если необходимо создайте новую группу')]
                                )
    cost = StringField("Стоимость в рублях", validators=[DataRequired()])
    sale = StringField('Скидка (- n Р)', validators=[DataRequired()], default='0')
    remains = StringField('Остаток продукта', validators=[DataRequired()])
    imgs = MultiCheckboxField('Изображение', choices=[(-1, 'Нет изображений')])
    img = MultipleFileField(validators=[])

    submit = SubmitField('Создать цвет продукта')

    def __init__(self, *args, product_groups=[], imgs_data=[], must_upload=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_group.choices.extend(product_groups)
        self.imgs.choices = imgs_data
        if not must_upload:
            self.img.validators = []