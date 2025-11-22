from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class AltaTipoHabitacionForm(FlaskForm):
    denominacion = StringField('Denominación', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    capacidad_personas = IntegerField('Capacidad de personas', validators=[DataRequired()])
    precio_por_noche = FloatField('Precio por noche ($)', validators=[DataRequired()])

    # Campo para subir archivo
    imagen = FileField('Imagen de la habitación', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'png', 'jpeg'], 'Solo imágenes jpg o png!')
    ])

    guardar = SubmitField('Guardar Alojamiento')