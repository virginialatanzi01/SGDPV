from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class CargarConsumoForm(FlaskForm):
    estadia_id = SelectField('Habitación / Huésped', coerce=int, validators=[DataRequired()])
    servicio_id = SelectField('Servicio', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', default=1, validators=[DataRequired(), NumberRange(min=1)])
    guardar = SubmitField('Registrar Consumo')