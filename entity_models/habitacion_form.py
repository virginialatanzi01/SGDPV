from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class HabiacionForm(FlaskForm):
    nro_habitacion = StringField('Número de habitacion', validators=[DataRequired()])
    guardar = SubmitField('Guardar')