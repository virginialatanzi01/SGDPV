from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField
from wtforms.validators import DataRequired

class BusquedaReservaForm(FlaskForm):
    fecha_desde = DateField('Fecha desde', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_hasta = DateField('Fecha hasta', format='%Y-%m-%d', validators=[DataRequired()])

    cantidad_personas = SelectField('Cantidad de personas',
                                    choices=[(i, str(i)) for i in range(1, 5)],
                                    coerce=int,
                                    validators=[DataRequired()])
    buscar = SubmitField('Buscar alojamiento')


class ModificarReservaForm(FlaskForm):
    fecha_desde = DateField('Fecha desde', format='%Y-%m-%d', validators=[DataRequired()])
    fecha_hasta = DateField('Fecha hasta', format='%Y-%m-%d', validators=[DataRequired()])
    cantidad_personas = SelectField('Cantidad de personas',
                                    choices=[(i, str(i)) for i in range(1, 5)],
                                    coerce=int,
                                    validators=[DataRequired()])

    guardar = SubmitField('Guardar cambios')

class ModificarEgresoForm(FlaskForm):
    fecha_egreso = DateField('Nueva Fecha de salida', format='%Y-%m-%d', validators=[DataRequired()])
    guardar = SubmitField('Actualizar salida')