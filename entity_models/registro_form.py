from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired

class RegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    tipo_documento = SelectField('Tipo de documento',
        choices=[('DNI', 'Documento Nacional de Identidad (DNI)'),('LE', 'Libreta de Enrolamiento (LE)'),('LC', 'Libreta Cívica (LC)')],
        validators=[DataRequired()]
        )
    nro_documento = StringField('Número de documento', validators=[DataRequired()])
    fecha_nacimiento = DateField('Fecha de nacimiento',
                                 format='%d-%m-%Y',
                                 validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    nombre_usuario = StringField('Usuario', validators=[DataRequired()])
    contrasena = PasswordField('Contraseña', validators=[DataRequired()])
    tipo_persona = SelectField('Tipo de persona',
        choices=[('administrador', 'Administrador'),('cliente', 'Cliente')],
        validators=[DataRequired()],
        default = 'administrador'
        )
    guardar = SubmitField('Guardar')