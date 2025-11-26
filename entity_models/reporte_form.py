from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, SelectField
from wtforms.validators import DataRequired
from datetime import date

class ReporteVentasForm(FlaskForm):
    fecha_desde = DateField('Fecha desde', format='%Y-%m-%d', default=date.today)
    fecha_hasta = DateField('Fecha hasta', format='%Y-%m-%d', default=date.today)
    submit = SubmitField('Filtrar ventas')

class ReporteOcupacionForm(FlaskForm):
    anio = SelectField('Año', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Actualizar gráfico')