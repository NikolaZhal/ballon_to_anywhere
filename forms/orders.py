from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, widgets, SelectMultipleField, DateField, \
    TextAreaField, RadioField, TimeField
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class BasketForm(FlaskForm):
    content = MultiCheckboxField('Label', choices=[(1, '1'), (2, '2')])
    submit = SubmitField('Сделать заказ')

    def __init__(self, *args, data=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.content.choices = data


class MakeOrder(FlaskForm):
    address = StringField('Адрес доставки', validators=[DataRequired()])
    date = DateField('Дата доставки', format='%Y-%m-%d')
    time = TimeField('Время доставки')
    description = TextAreaField('Комментарии к заказу', validators=[DataRequired()])
    how_pay = RadioField('Способ оплаты', coerce=int, choices=[(0, 'Картой на сайте'), (1, 'При получении')])
    submit = SubmitField('Заказать')
