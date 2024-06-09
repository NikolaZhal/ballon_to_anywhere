from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, MultipleFileField, widgets, SelectMultipleField, \
    TextAreaField, IntegerField, RadioField
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SearchForm(FlaskForm):
    min_cost = StringField('Цена От', validators=[], default='0')
    max_cost = StringField('Цена До', validators=[])
    types = MultiCheckboxField('Типы товаров', coerce=int, choices=[(-1, 'Все')])
    submit = SubmitField('Показать')

    def __init__(self, *args, types_data=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.types.choices.extend(types_data)


class ProductGroupForm(FlaskForm):
    title = StringField('Название продукта (цветовой группы)', validators=[DataRequired()])
    description = TextAreaField('Описание продукта (цветовой группы)', validators=[DataRequired()])
    type = SelectField('Тип продукта (цветовой группы)', coerce=int, choices=[(-1, 'Если необходимо создайте тип')])
    submit = SubmitField('Подтвердить')

    def __init__(self, *args, types=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.type.choices = types


class ProductForm(FlaskForm):
    color = StringField('Цвет продукта (единицы цветовой группы)', validators=[DataRequired()])
    product_group = SelectField('Наименование группы товара', coerce=int,
                                choices=[(-1, 'Если необходимо создайте новую группу')]
                                )
    cost = IntegerField("Стоимость в рублях", validators=[DataRequired()])
    sale = IntegerField('Скидка (- n Р)', validators=[], default=0)
    remains = IntegerField('Остаток продукта', validators=[DataRequired()])
    imgs = MultiCheckboxField('Изображение', choices=[(-1, 'Нет изображений')])
    img = MultipleFileField(validators=[])
    categories = MultiCheckboxField(validators=[])

    submit = SubmitField('Подтвердить')

    def __init__(self, *args, product_groups=[], imgs_data=[], categories=[], must_upload=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.product_group.choices.extend(product_groups)
        self.imgs.choices = imgs_data
        self.categories.choices = categories
        if not must_upload:
            self.img.validators = []


class CommentsForm(FlaskForm):
    plus = StringField('Плюсы товара', validators=[])
    minus = StringField('Минусы товара', validators=[])
    content = StringField('Комментарий', validators=[])
    mark = RadioField("Оценка от 0 до 5", coerce=int, choices=[(i, f'{i}') for i in range(1, 6)], validators=[DataRequired()])
    submit = SubmitField('Отправить')