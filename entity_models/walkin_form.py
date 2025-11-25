from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import date

class WalkinForm(FlaskForm):
    # La fecha de ingreso es implícitamente HOY, solo se solicita salida
    fecha_egreso = DateField('Fecha de Salida', format='%Y-%m-%d', validators=[DataRequired()])
    cantidad_personas = IntegerField('Personas', validators=[DataRequired(), NumberRange(min=1, max=5)])
    buscar = SubmitField('Buscar Disponibilidad')