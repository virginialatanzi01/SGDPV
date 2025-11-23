import ast
import random
from datetime import datetime, timedelta, date

from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from flask_mail import Message, Mail
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import ObjectDeletedError, StaleDataError
from werkzeug.exceptions import NotFound

from data.database import Database
from entity_models.persona_model import Persona
from entity_models.registro_cliente_form import RegistroClienteForm
from entity_models.registro_form import RegistroForm
from entity_models.formularios_edicion import EditarDatosForm, CambiarContrasenaForm
from entity_models.reserva_form import BusquedaReservaForm
from entity_models.tipo_habitacion_model import TipoHabitacion
from entity_models.habitacion_model import Habitacion
from logic.tipo_habitacion_logic import TipoHabitacionLogic
from logic.persona_logic import PersonaLogic
from logic.persona_logic import PersonaLogic
app = Flask(__name__)

# Base de Datos
app.config['SQLALCHEMY_DATABASE_URI'] = Database.configura_conexion()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'konigari'

# Configuración de Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'konigari2023'
app.config['MAIL_PASSWORD'] = 'nrez dpvc rino mqjw'
app.config['MAIL_DEFAULT_SENDER'] = 'konigari2023@gmail.com'
app.config['CARRITO'] = []

# Extensiones
mail = Mail(app)
Database.db.init_app(app)
migrate = Migrate(app, Database.db)

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
        return render_template('home.html',
                               persona_logueada=persona_logueada)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('persona_logueada', None)
    return redirect(url_for('login'))

@app.route('/get_all_personas')
def get_all_personas():
    persona_logueada = obtener_persona_logueada()
    if persona_logueada.tipo_persona == 'administrador':
        personas = PersonaLogic.get_all_personas()
        return render_template('listado_personas.html', personas_param=personas,
                               titulo='Personas')
    else:
        return render_template('mensaje.html',
                               mensaje='Página no encontrada',
                               persona_logueada=persona_logueada)

@app.route('/get_all_clientes')
def get_all_clientes():
    persona_logueada = obtener_persona_logueada()
    if persona_logueada.tipo_persona == 'administrador':
        clientes = PersonaLogic.get_all_clientes()
        return render_template('listado_personas.html', personas_param=clientes,
                               titulo='Clientes')
    else:
        return render_template('mensaje.html',
                               mensaje='Página no encontrada',
                               persona_logueada=persona_logueada)

@app.route('/eliminar_persona/<int:id>')
def delete_persona(id):
    persona_logueada = obtener_persona_logueada()
    if persona_logueada.tipo_persona == 'administrador':
        try:
            PersonaLogic.delete_persona(id)
            return render_template('mensaje.html',
                                   mensaje='Persona eliminada correctamente',
                                   persona_logueada=persona_logueada)
        except IntegrityError as e:
            raise e
        except ObjectDeletedError as e:
            raise e
        except StaleDataError as e:
            raise e
    else:
        return render_template('mensaje.html',
                               mensaje='Página no encontrada',
                               persona_logueada=persona_logueada)

@app.route('/agregar_persona', methods=['GET', 'POST'])
def add_persona():
    persona_logueada = obtener_persona_logueada()

    # CASO 1: Admin agrega persona
    if persona_logueada is not None and persona_logueada.tipo_persona == 'administrador':
        persona = Persona()
        registro_form = RegistroForm(obj=persona)
        if request.method == 'POST':
            contrasena = request.form['contrasena']
            nombre_usuario = request.form['nombre_usuario']

            if registro_form.validate_on_submit():
                if PersonaLogic.get_persona_by_user(nombre_usuario):
                    return render_template('mensaje.html',
                                           mensaje='Error: Nombre de usuario ya existente',
                                           persona_logueada=persona_logueada)
                else:
                    registro_form.populate_obj(persona)
                    PersonaLogic.add_persona(persona, contrasena)
                    return render_template('mensaje.html',
                                           mensaje='Persona agregada correctamente',
                                           persona_logueada=persona_logueada)
            else:
                return render_template('mensaje.html',
                                       mensaje='Error al agregar persona',
                                       persona_logueada=persona_logueada)
        return render_template('alta_persona.html',
                               persona_agregar=registro_form,
                               persona_logueada=persona_logueada)

    # CASO 2: Usuario logueado pero no es admin (Error)
    elif persona_logueada is not None:
        return render_template('mensaje.html',
                               mensaje='Página no encontrada',
                               persona_logueada=persona_logueada)

    # CASO 3: Registro Público (Cliente)
    else:
        administradores = PersonaLogic.get_all_administradores()
        # Primer uso del sistema (crear admin)
        if len(administradores) == 0:
            persona = Persona()
            registro_form = RegistroForm(obj=persona)
            if request.method == 'POST':
                contrasena = request.form['contrasena']
                nombre_usuario = request.form['nombre_usuario']
                if registro_form.validate_on_submit():
                    if PersonaLogic.get_persona_by_user(nombre_usuario):
                        return render_template('mensaje.html',
                                               mensaje='Error: Nombre de usuario ya existente',
                                               persona_logueada=persona_logueada)
                    else:
                        registro_form.populate_obj(persona)
                        PersonaLogic.add_persona(persona, contrasena)
                        return render_template('mensaje.html',
                                               mensaje='Persona agregada correctamente',
                                               persona_logueada=persona_logueada)
            return render_template('alta_persona.html',
                                   persona_agregar=registro_form,
                                   persona_logueada=persona_logueada)
        # Registro normal de cliente público
        else:
            persona = Persona()
            registro_cliente_form = RegistroClienteForm(obj=persona)
            if request.method == 'POST':
                contrasena = request.form['contrasena']
                nombre_usuario = request.form['nombre_usuario']
                if registro_cliente_form.validate_on_submit():
                    if PersonaLogic.get_persona_by_user(nombre_usuario):
                        return render_template('mensaje.html',
                                               mensaje='Error: Nombre de usuario ya existente',
                                               persona_logueada=persona_logueada)
                    else:
                        registro_cliente_form.populate_obj(persona)
                        persona.tipo_persona = 'cliente'
                        PersonaLogic.add_persona(persona, contrasena)
                        return render_template('mensaje.html',
                                               mensaje='Se ha registrado correctamente. Por favor inicie sesión.',
                                               persona_logueada=persona_logueada)
                else:
                    return render_template('mensaje.html',
                                           mensaje='Error al registrarse',
                                           persona_logueada=persona_logueada)
            else:
                return render_template('alta_persona.html',
                                       persona_agregar=registro_cliente_form,
                                       persona_logueada=persona_logueada)

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
        else:
            print("Errores validación:", form.errors)

    return render_template('editar_datos_personales.html',
                           form=form,
                           persona_logueada=persona_logueada)

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
                                       persona_logueada=persona_logueada)
            except Exception as e:
                app.logger.error(f"Error pass: {e}")
                return render_template('mensaje.html', mensaje='Error al cambiar contraseña')

    return render_template('cambiar_contrasena.html',
                           form=form,
                           persona_logueada=persona_logueada)

@app.route('/validar_nombre_usuario', methods=['POST'])
def validar_nombre_usuario():
    nombre_usuario = request.form.get('nombre_usuario')
    if PersonaLogic.get_persona_by_user(nombre_usuario) is not None:
        existe = True
    else:
        existe = False
    return jsonify({'existe': existe})

@app.route('/read_datos_persona/<int:id>', methods=['GET'])
def read_datos_persona(id):
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return render_template('mensaje.html', mensaje='Usuario no autenticado')
    if id != persona_logueada.id:
        return render_template('mensaje.html', mensaje='Acceso no autorizado')
    if persona_logueada.fecha_nacimiento:
        fecha_str = str(persona_logueada.fecha_nacimiento)
        try:
            if "GMT" in fecha_str:
                fecha_obj = datetime.strptime(fecha_str, '%a, %d %b %Y %H:%M:%S %Z')
                persona_logueada.fecha_nacimiento = fecha_obj.strftime('%d-%m-%Y')
            elif hasattr(persona_logueada.fecha_nacimiento, 'strftime'):
                persona_logueada.fecha_nacimiento = persona_logueada.fecha_nacimiento.strftime('%d-%m-%Y')
        except ValueError:
            pass
    return render_template('read_datos_persona.html', persona=persona_logueada, persona_logueada=persona_logueada)


@app.route('/reservar_alojamiento', methods=['GET', 'POST'])
def reservar_alojamiento():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'cliente':
        return redirect(url_for('login'))
    form = BusquedaReservaForm()
    fecha_hoy = date.today().strftime('%Y-%m-%d')
    if request.method == 'POST' and form.validate_on_submit():
        fecha_desde = form.fecha_desde.data
        fecha_hasta = form.fecha_hasta.data
        cant_personas = form.cantidad_personas.data
        if fecha_desde < date.today():
            return render_template('reservar_alojamiento.html',
                                   form=form,
                                   persona_logueada=persona_logueada,
                                   hoy=fecha_hoy,
                                   error="La fecha de ingreso no puede ser en el pasado.")
        if fecha_hasta <= fecha_desde:
            return render_template('reservar_alojamiento.html',
                                   form=form,
                                   persona_logueada=persona_logueada,
                                   hoy=fecha_hoy,
                                   error="La fecha de salida debe ser posterior a la de ingreso.")
        delta = fecha_hasta - fecha_desde
        cantidad_noches = delta.days
        resultados = TipoHabitacionLogic.buscar_tipos_disponibles(fecha_desde, fecha_hasta, cant_personas)
        return render_template('resultados_busqueda.html',
                               persona_logueada=persona_logueada,
                               resultados=resultados,
                               cantidad_noches=cantidad_noches,
                               fecha_desde=fecha_desde,
                               fecha_hasta=fecha_hasta)
    return render_template('reservar_alojamiento.html',
                           form=form,
                           persona_logueada=persona_logueada,
                           hoy=fecha_hoy)

if __name__ == '__main__':
    app.run(debug=True)