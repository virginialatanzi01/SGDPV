from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField
from wtforms.validators import DataRequired

class BusquedaReservaForm(FlaskForm):
    fecha_desde = DateField('Fecha Desde', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_hasta = DateField('Fecha Hasta', format='%Y-%m-%d', validators=[DataRequired()])

    cantidad_personas = SelectField('Cantidad de Personas',
                                    choices=[(i, str(i)) for i in range(1, 6)],
                                    coerce=int,
                                    validators=[DataRequired()])

    buscar = SubmitField('Buscar Alojamiento')