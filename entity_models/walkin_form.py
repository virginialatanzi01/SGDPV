from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField
from wtforms.validators import DataRequired
from datetime import date

class WalkinForm(FlaskForm):
    # La fecha de ingreso es implícitamente HOY, solo pedimos salida
    fecha_egreso = DateField('Fecha de salida', format='%Y-%m-%d', validators=[DataRequired()])
    cantidad_personas = SelectField('Cantidad de personas',
                                    choices=[(i, str(i)) for i in range(1, 5)],
                                    coerce=int,
                                    validators=[DataRequired()])
    buscar = SubmitField('Buscar disponibilidad')