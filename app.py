import os
from datetime import datetime

from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from flask_mail import Mail
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from data.database import Database
from entity_models.persona_model import Persona
from entity_models.registro_cliente_form import RegistroClienteForm
from entity_models.registro_form import RegistroForm
from entity_models.formularios_edicion import EditarDatosForm, CambiarContrasenaForm
from entity_models.tipo_habitacion_form import AltaTipoHabitacionForm  # Nuevo
from logic.persona_logic import PersonaLogic
from logic.tipo_habitacion_logic import TipoHabitacionLogic  # Nuevo
app = Flask(__name__)

# 1. Configuración de Base de Datos
app.config['SQLALCHEMY_DATABASE_URI'] = Database.configura_conexion()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'konigari'

# 2. Configuración de Carpeta de Imágenes
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'imagenes_tipos_habitaciones')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 3. Extensiones
Database.db.init_app(app)
migrate = Migrate(app, Database.db)  # Esto permite actualizar la BD sin borrar datos
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'konigari2023'
app.config['MAIL_PASSWORD'] = 'nrez dpvc rino mqjw'
app.config['MAIL_DEFAULT_SENDER'] = 'konigari2023@gmail.com'

def obtener_persona_logueada():
    persona_data = session.get('persona_logueada')
    if persona_data:
        return Persona.from_dict(persona_data)
    return None

# --- RUTAS ---
@app.route('/')
@app.route('/inicio')
def inicio():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        persona_logueada = obtener_persona_logueada()
        if persona_logueada:
            return redirect(url_for('home'))
        if request.method == 'POST':
            nombre_usuario = request.form['nombre_usuario']
            contrasena = request.form['contrasena']
            persona = PersonaLogic.valida_credenciales(nombre_usuario, contrasena)
            if persona:
                session['persona_logueada'] = persona.to_dict()
                return redirect(url_for('home'))
            else:
                return render_template('mensaje.html', mensaje='Usuario o contraseña incorrecto/s',
                                       persona_logueada=None)
        else:
            return render_template('login.html')
    except Exception as e:
        app.logger.error(f"Error en /login: {e}")
        return render_template('mensaje.html', mensaje='Ocurrió un error inesperado.', persona_logueada=None)

@app.route('/home')
def home():
    persona_logueada = obtener_persona_logueada()
    if persona_logueada:
        return render_template('home.html', persona_logueada=persona_logueada)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('persona_logueada', None)
    return redirect(url_for('login'))

@app.route('/editar_datos_personales', methods=['GET', 'POST'])
def editar_datos_personales():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return redirect(url_for('login'))
    persona_db = PersonaLogic.get_one_persona(persona_logueada.id)
    form = EditarDatosForm(obj=persona_db)
    if request.method == 'POST':
        if form.validate_on_submit():
            form.populate_obj(persona_db)
            try:
                PersonaLogic.update_persona(persona_db, contrasena=None)
                session['persona_logueada'] = persona_db.to_dict()
                return render_template('mensaje.html',
                                       mensaje='Datos personales actualizados correctamente',
                                       url_volver=url_for('read_datos_persona', id=persona_db.id),
                                       texto_boton='Volver a Mi Cuenta',
                                       persona_logueada=persona_db)
            except Exception as e:
                app.logger.error(f"Error al actualizar: {e}")
                return render_template('mensaje.html', mensaje='Error al actualizar los datos')
    return render_template('editar_datos_personales.html', form=form, persona_logueada=persona_logueada)

@app.route('/cambiar_contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return redirect(url_for('login'))
    persona_db = PersonaLogic.get_one_persona(persona_logueada.id)
    form = CambiarContrasenaForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                nueva_pass = form.nueva_contrasena.data
                PersonaLogic.update_persona(persona_db, contrasena=nueva_pass)
                return render_template('mensaje.html',
                                       mensaje='Contraseña actualizada con éxito',
                                       url_volver=url_for('read_datos_persona', id=persona_db.id),
                                       texto_boton='Volver a Mi Cuenta',
                                       persona_logueada=persona_db)
            except Exception as e:
                app.logger.error(f"Error pass: {e}")
                return render_template('mensaje.html', mensaje='Error al cambiar contraseña')

    return render_template('cambiar_contrasena.html', form=form, persona_logueada=persona_logueada)

@app.route('/read_datos_persona/<int:id>', methods=['GET'])
def read_datos_persona(id):
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return render_template('mensaje.html', mensaje='Usuario no autenticado')
    if id != persona_logueada.id:
        return render_template('mensaje.html', mensaje='Acceso no autorizado')
    if persona_logueada.fecha_nacimiento:
        try:
            fecha_str = str(persona_logueada.fecha_nacimiento)
            if len(fecha_str) > 10:
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
            else:
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d')
            persona_logueada.fecha_nacimiento = fecha_obj.strftime('%d/%m/%Y')
        except ValueError:
            pass
    return render_template('read_datos_persona.html', persona=persona_logueada, persona_logueada=persona_logueada)

@app.route('/validar_nombre_usuario', methods=['POST'])
def validar_nombre_usuario():
    nombre_usuario = request.form.get('nombre_usuario')
    existe = PersonaLogic.get_persona_by_user(nombre_usuario) is not None
    return jsonify({'existe': existe})

@app.route('/agregar_persona', methods=['GET', 'POST'])
def add_persona():
    persona_logueada = obtener_persona_logueada()
    if persona_logueada and persona_logueada.tipo_persona == 'administrador':
        persona = Persona()
        form = RegistroForm(obj=persona)
        if request.method == 'POST' and form.validate_on_submit():
            if PersonaLogic.get_persona_by_user(form.nombre_usuario.data):
                return render_template('mensaje.html', mensaje='Error: Usuario ya existe')
            form.populate_obj(persona)
            PersonaLogic.add_persona(persona, form.contrasena.data)
            return render_template('mensaje.html', mensaje='Persona agregada correctamente')
        return render_template('alta_persona.html', persona_agregar=form, persona_logueada=persona_logueada)
    else:
        persona = Persona()
        form = RegistroClienteForm(obj=persona)
        if request.method == 'POST' and form.validate_on_submit():
            if PersonaLogic.get_persona_by_user(form.nombre_usuario.data):
                return render_template('mensaje.html', mensaje='Error: Usuario ya existe')
            form.populate_obj(persona)
            PersonaLogic.add_persona(persona, form.contrasena.data)
            return render_template('mensaje.html', mensaje='Registro exitoso. Inicia sesión.')
        return render_template('alta_persona.html', persona_agregar=form, persona_logueada=None)

@app.route('/gestionar_alojamientos')
def gestionar_alojamientos():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return redirect(url_for('home'))
    lista = TipoHabitacionLogic.get_all_tipos()
    return render_template('gestionar_alojamientos.html', alojamientos=lista, persona_logueada=persona_logueada)

@app.route('/crear_alojamiento', methods=['GET', 'POST'])
def crear_alojamiento():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return redirect(url_for('home'))
    form = AltaTipoHabitacionForm()
    if form.validate_on_submit():
        f = form.imagen.data
        nombre_archivo = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
        TipoHabitacionLogic.add_tipo_habitacion(
            denominacion=form.denominacion.data,
            descripcion=form.descripcion.data,
            capacidad_personas=form.capacidad.data,
            precio_por_noche=form.precio_por_noche.data,
            nombre_imagen=nombre_archivo
        )
        return redirect(url_for('gestionar_alojamientos'))
    return render_template('crear_alojamiento.html', form=form, persona_logueada=persona_logueada)

if __name__ == '__main__':
    app.run(debug=True)