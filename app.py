import ast
import random
from datetime import datetime, timedelta

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
from logic.persona_logic import PersonaLogic
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Database.configura_conexion()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'konigari'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'konigari2023'
app.config['MAIL_PASSWORD'] = 'nrez dpvc rino mqjw'
app.config['MAIL_DEFAULT_SENDER'] = 'konigari2023@gmail.com'
app.config['CARRITO'] = []

mail = Mail(app)
Database.db.init_app(app)
migrate = Migrate()
migrate.init_app(app, Database.db)

# Función para obtener la persona logueada en la sesión
def obtener_persona_logueada():
    # Obtiene a la persona que está logueada en la sesión
    persona_data = session.get('persona_logueada')
    if persona_data:
        persona_logueada = Persona.from_dict(persona_data)
        return persona_logueada
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
                return redirect(url_for('home'))  # Cambia a redirigir para evitar reenvíos
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
    # A la persona que guardé en la sesión en el metodo login(), accede desde este metodo
    persona_logueada = obtener_persona_logueada()
    if persona_logueada:
        return render_template('home.html',
                               persona_logueada=persona_logueada)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Elimino los datos de la sesión de la persona
    session.pop('persona_logueada', None)
    # Elimino el carrito
    #app.config['CARRITO'] = []
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


from flask import request, render_template
from sqlalchemy.exc import IntegrityError


@app.route('/agregar_persona', methods=['GET', 'POST'])
def add_persona():
    persona_logueada = obtener_persona_logueada()
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
    elif persona_logueada is not None:
        return render_template('mensaje.html',
                               mensaje='Página no encontrada',
                               persona_logueada=persona_logueada)
    else:
        administradores = PersonaLogic.get_all_administradores()
        if len(administradores) == 0:
            persona = Persona()
            registro_form = RegistroForm(obj=persona)
            if request.method == 'POST':
                contrasena = request.form['contrasena']
                nombre_usuario = request.form['nombre_usuario']
                try:
                    if registro_form.fecha_nacimiento.data:
                        fecha_str = registro_form.fecha_nacimiento.data.strftime('%d-%m-%Y')
                        fecha_nacimiento = datetime.strptime(fecha_str, '%d-%m-%Y').date()
                        persona.fecha_nacimiento = fecha_nacimiento
                except ValueError:
                    return render_template('mensaje.html',
                                           mensaje='Error: Formato de fecha inválido. Usa DD-MM-YYYY',
                                           persona_logueada=persona_logueada)

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
                        PersonaLogic.add_persona(persona, contrasena)
                        return render_template('mensaje.html',
                                               mensaje='Se ha registrado correctamente',
                                               persona_logueada=persona_logueada)
                else:
                    return render_template('mensaje.html',
                                           mensaje='Error al registrarse',
                                           persona_logueada=persona_logueada)
            else:
                persona = Persona()
                registro_cliente_form = RegistroClienteForm(obj=persona)
                return render_template('alta_persona.html',
                                       persona_agregar=registro_cliente_form,
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
        try:
            fecha_original = datetime.strptime(persona_logueada.fecha_nacimiento, '%a, %d %b %Y %H:%M:%S GMT')
            persona_logueada.fecha_nacimiento = fecha_original.strftime('%d/%m/%Y')
        except ValueError:
            persona_logueada.fecha_nacimiento = "Formato inválido"
    return render_template('read_datos_persona.html', persona=persona_logueada, persona_logueada=persona_logueada)