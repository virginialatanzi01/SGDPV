from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class OlvideContrasenaForm(FlaskForm):
    email = StringField('Email registrado', validators=[DataRequired(), Email()])
    enviar = SubmitField('Enviar enlace')

class RestablecerContrasenaForm(FlaskForm):
    nueva_contrasena = PasswordField('Nueva contraseña', validators=[
        DataRequired(),
        EqualTo('confirmar_contrasena', message='Las contraseñas deben coincidir')
    ])
    confirmar_contrasena = PasswordField('Repetir contraseña', validators=[DataRequired()])
    guardar = SubmitField('Cambiar contraseña')