from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class BusquedaClienteForm(FlaskForm):
    nro_documento = StringField('DNI del Cliente', validators=[DataRequired()])
    buscar = SubmitField('Buscar Reservas')