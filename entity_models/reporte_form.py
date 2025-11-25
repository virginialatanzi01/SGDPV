from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, SelectField
from wtforms.validators import DataRequired
from datetime import date

class ReporteVentasForm(FlaskForm):
    fecha_desde = DateField('Fecha Desde', format='%Y-%m-%d', default=date.today)
    fecha_hasta = DateField('Fecha Hasta', format='%Y-%m-%d', default=date.today)
    buscar = SubmitField('Generar Reporte')

class ReporteOcupacionForm(FlaskForm):
    anio = SelectField('Año', coerce=int, validators=[DataRequired()])
    buscar = SubmitField('Ver Gráfico')