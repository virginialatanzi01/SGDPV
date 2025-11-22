from flask_wtf import FlaskForm
from wtforms import StringField, DateField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, EqualTo

# Formulario para datos personales
class EditarDatosForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    tipo_documento = SelectField('Tipo de documento',
        choices=[('DNI', 'Documento Nacional de Identidad (DNI)'),('LE', 'Libreta de Enrolamiento (LE)'),('LC', 'Libreta Cívica (LC)')],
        validators=[DataRequired()]
    )
    nro_documento = StringField('Número de documento', validators=[DataRequired()])
    fecha_nacimiento = DateField('Fecha de nacimiento', format='%d-%m-%Y', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    nombre_usuario = StringField('Usuario', validators=[DataRequired()])
    # Nota: No incluimos contraseña aquí
    guardar = SubmitField('Guardar Cambios')

# Formulario para datos de usuario (solo contraseña)
class CambiarContrasenaForm(FlaskForm):
    nueva_contrasena = PasswordField('Nueva Contraseña', validators=[
        DataRequired(),
        EqualTo('confirmar_contrasena', message='Las contraseñas deben coincidir')
    ])
    confirmar_contrasena = PasswordField('Repetir Nueva Contraseña', validators=[DataRequired()])
    guardar = SubmitField('Actualizar Contraseña')