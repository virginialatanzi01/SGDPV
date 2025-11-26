import ast
import random
from threading import Thread
from flask_mail import Mail, Message
import calendar
from datetime import datetime, timedelta, date
from flask import Flask, render_template, url_for, redirect, request, session, jsonify
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import ObjectDeletedError, StaleDataError
from werkzeug.exceptions import NotFound

from data.database import Database

from entity_models.persona_model import Persona
from entity_models.registro_cliente_form import RegistroClienteForm
from entity_models.registro_form import RegistroForm
from entity_models.formularios_edicion import EditarDatosForm, CambiarContrasenaForm
from entity_models.reserva_form import BusquedaReservaForm, ModificarReservaForm, ModificarEgresoForm
from entity_models.tipo_habitacion_model import TipoHabitacion
from entity_models.habitacion_model import Habitacion
from entity_models.estadia_model import Estadia
from entity_models.busqueda_cliente_form import BusquedaClienteForm
from entity_models.servicio_model import Servicio
from entity_models.consumo_model import Consumo
from entity_models.consumo_form import CargarConsumoForm
from entity_models.walkin_form import WalkinForm
from entity_models.reporte_form import ReporteVentasForm, ReporteOcupacionForm

from logic.tipo_habitacion_logic import TipoHabitacionLogic
from logic.persona_logic import PersonaLogic
from logic.estadia_logic import EstadiaLogic
from logic.habitacion_logic import HabitacionLogic
from logic.servicio_logic import ServicioLogic
from logic.email_logic import EmailLogic  # <--- ¡AGREGADO IMPORTANTE!

app = Flask(__name__)

# Base de Datos
app.config['SQLALCHEMY_DATABASE_URI'] = Database.configura_conexion()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'konigari'

#Email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'vl.alojamientos@gmail.com'
app.config['MAIL_PASSWORD'] = 'rcmq iphd enoz nuhv' # Tu clave generada
app.config['MAIL_DEFAULT_SENDER'] = ('VL Alojamientos', 'vl.alojamientos@gmail.com')

# Extensiones
mail = Mail(app)
# Función para enviar emails en segundo plano
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error enviando email: {e}")

# Helper para llamar desde la lógica
def enviar_correo_async(asunto, destinatarios, template_html):
    msg = Message(asunto, recipients=destinatarios)
    msg.html = template_html
    Thread(target=send_async_email, args=(app, msg)).start()

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
                    EmailLogic.enviar_bienvenida_registro(persona)
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
                    EmailLogic.enviar_bienvenida_registro(persona)
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
            return render_template('reservar_alojamiento.html', form=form, persona_logueada=persona_logueada,
                                   hoy=fecha_hoy, error="La fecha de ingreso no puede ser en el pasado.")
        if fecha_hasta <= fecha_desde:
            return render_template('reservar_alojamiento.html', form=form, persona_logueada=persona_logueada,
                                   hoy=fecha_hoy, error="La fecha de salida debe ser posterior a la de ingreso.")
        delta = fecha_hasta - fecha_desde
        cantidad_noches = delta.days
        ideales, otros = TipoHabitacionLogic.buscar_tipos_disponibles(fecha_desde, fecha_hasta, cant_personas)
        return render_template('resultados_busqueda.html',
                               persona_logueada=persona_logueada,
                               resultados_ideales=ideales,  # Pasamos ideales
                               resultados_otros=otros,  # Pasamos otros
                               cantidad_noches=cantidad_noches,
                               fecha_desde=fecha_desde,
                               fecha_hasta=fecha_hasta,
                               cantidad_personas=cant_personas)
    return render_template('reservar_alojamiento.html', form=form, persona_logueada=persona_logueada, hoy=fecha_hoy)

@app.route('/previsualizar_reserva', methods=['POST'])
def previsualizar_reserva():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return redirect(url_for('login'))
    tipo_id = request.form['tipo_id']
    fecha_desde = request.form['fecha_desde']
    fecha_hasta = request.form['fecha_hasta']
    precio_total = request.form['precio_total']
    cantidad_noches = request.form['cantidad_noches']
    cantidad_personas = request.form['cantidad_personas']
    tipo_habitacion = TipoHabitacionLogic.get_one_tipo(tipo_id)
    return render_template('resumen_reserva.html',
                           persona=persona_logueada,
                           tipo=tipo_habitacion,
                           fecha_desde=fecha_desde,
                           fecha_hasta=fecha_hasta,
                           precio_total=precio_total,
                           cantidad_noches=cantidad_noches,
                           cantidad_personas = cantidad_personas)


@app.route('/confirmar_reserva', methods=['POST'])
def confirmar_reserva():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return redirect(url_for('login'))
    tipo_id = request.form['tipo_id']
    fecha_desde = datetime.strptime(request.form['fecha_desde'], '%Y-%m-%d').date()
    fecha_hasta = datetime.strptime(request.form['fecha_hasta'], '%Y-%m-%d').date()
    precio_total = float(request.form['precio_total'])
    cantidad_personas = int(request.form['cantidad_personas'])
    try:
        reserva = EstadiaLogic.crear_reserva(
            persona_id=persona_logueada.id,
            tipo_id=tipo_id,
            f_ingreso=fecha_desde,
            f_egreso=fecha_hasta,
            precio_total=precio_total,
            cantidad_personas=cantidad_personas
        )
        EmailLogic.enviar_confirmacion_reserva(reserva)
        tipo_habitacion = TipoHabitacionLogic.get_one_tipo(tipo_id)
        return render_template('comprobante_reserva.html',
                               persona=persona_logueada,
                               reserva=reserva,
                               tipo=tipo_habitacion)
    except Exception as e:
        app.logger.error(f"Error al reservar: {e}")
        return render_template('mensaje.html', mensaje="Ocurrió un error al procesar la reserva.")


@app.route('/mis_reservas')
def mis_reservas():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return redirect(url_for('login'))
    pendientes, historicas = EstadiaLogic.get_mis_reservas(persona_logueada.id)
    return render_template('mis_reservas.html',
                           persona_logueada=persona_logueada,
                           pendientes=pendientes,
                           historicas=historicas)


@app.route('/cancelar_reserva/<int:id>')
def cancelar_reserva(id):
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return redirect(url_for('login'))
    try:
        reserva = EstadiaLogic.get_one_estadia(id)
        if reserva.persona_id != persona_logueada.id:
            return render_template('mensaje.html', mensaje="Acceso no autorizado")
        EstadiaLogic.cancelar_reserva(id)
        EmailLogic.enviar_notificacion_cancelacion(reserva)
        return redirect(url_for('mis_reservas'))
    except Exception as e:
        app.logger.error(f"Error al cancelar: {e}")
        return render_template('mensaje.html', mensaje="Error al cancelar la reserva")

@app.route('/modificar_reserva/<int:id>', methods=['GET', 'POST'])
def modificar_reserva(id):
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return redirect(url_for('login'))
    reserva = EstadiaLogic.get_one_estadia(id)
    # Seguridad: verificar dueño
    if reserva.persona_id != persona_logueada.id:
        return render_template('mensaje.html', mensaje="Acceso no autorizado")
    # Solo se pueden modificar reservas en estado 'Reservada'
    if reserva.estado != 'Reservada':
        return render_template('mensaje.html', mensaje="No se puede modificar una reserva que no esté pendiente.")
    form = ModificarReservaForm(obj=reserva)
    if request.method == 'GET':
        form.fecha_desde.data = reserva.fecha_ingreso
        form.fecha_hasta.data = reserva.fecha_egreso
        form.cantidad_personas.data = reserva.cantidad_personas
    fecha_hoy = date.today().strftime('%Y-%m-%d')
    if request.method == 'POST' and form.validate_on_submit():
        nueva_cantidad_personas = form.cantidad_personas.data
        # 1. Validar Personas vs Capacidad Habitación
        if form.cantidad_personas.data > reserva.tipo_habitacion.capacidad_personas:
            error_msg = f"Esta habitación ({reserva.tipo_habitacion.denominacion}) solo permite hasta {reserva.tipo_habitacion.capacidad_personas} personas. Para más personas, cancele y reserve otra."
            return render_template('modificar_reserva.html', form=form, reserva=reserva, hoy=fecha_hoy, error=error_msg,
                                   persona_logueada=persona_logueada)
        # 2. Validar Fechas
        f_desde = form.fecha_desde.data
        f_hasta = form.fecha_hasta.data
        if f_desde < date.today():
            return render_template('modificar_reserva.html', form=form, reserva=reserva, hoy=fecha_hoy,
                                   error="La fecha no puede ser pasada.", persona_logueada=persona_logueada)
        if f_hasta <= f_desde:
            return render_template('modificar_reserva.html', form=form, reserva=reserva, hoy=fecha_hoy,
                                   error="La salida debe ser posterior al ingreso.", persona_logueada=persona_logueada)
        # 3. Intentar Modificar (Lógica valida disponibilidad)
        exito, mensaje = EstadiaLogic.modificar_reserva(id, f_desde, f_hasta, nueva_cantidad_personas)
        if exito:
            return render_template('mensaje.html',
                                   mensaje="Reserva modificada exitosamente",
                                   url_volver=url_for('mis_reservas'),
                                   texto_boton="Volver a Mis Reservas")
        else:
            return render_template('modificar_reserva.html', form=form, reserva=reserva, hoy=fecha_hoy, error=mensaje,
                                   persona_logueada=persona_logueada)
    return render_template('modificar_reserva.html',
                           form=form,
                           reserva=reserva,
                           hoy=fecha_hoy,
                           persona_logueada=persona_logueada)


@app.route('/admin/checkin', methods=['GET', 'POST'])
def admin_checkin():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return render_template('mensaje.html', mensaje='Acceso denegado')
    EstadiaLogic.procesar_no_shows()
    form = BusquedaClienteForm()
    reservas = None
    dni_buscado = None
    cliente_encontrado = None
    hoy = date.today()
    if request.method == 'POST' and form.validate_on_submit():
        dni_buscado = form.nro_documento.data
        reservas = EstadiaLogic.buscar_reservas_por_dni(dni_buscado)
        from logic.persona_logic import PersonaLogic
        cliente_encontrado = Persona.query.filter_by(nro_documento=dni_buscado).first()

    return render_template('admin_checkin_buscar.html',
                           persona_logueada=persona_logueada,
                           form=form,
                           reservas=reservas,
                           dni_buscado=dni_buscado,
                           cliente_encontrado=cliente_encontrado,
                           hoy=hoy)


@app.route('/admin/early_checkin/<int:reserva_id>')
def admin_early_checkin(reserva_id):
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return redirect(url_for('login'))
    reserva = EstadiaLogic.get_one_estadia(reserva_id)
    hoy = date.today()
    habitacion_asignada = HabitacionLogic.get_habitacion_disponible_by_tipo(
        reserva.tipo_habitacion_id,
        hoy,
        reserva.fecha_egreso
    )
    if habitacion_asignada:
        nuevo_precio = EstadiaLogic.calcular_nuevo_total_early_checkin(reserva_id)
        reserva.fecha_ingreso = hoy
        reserva.precio_total = nuevo_precio
        reserva.estado = 'En curso'
        reserva.habitacion_id = habitacion_asignada.id
        from data.data_estadia import DataEstadia
        DataEstadia.update_estadia()
        return render_template('admin_checkin_exitoso.html',
                               persona_logueada=persona_logueada,
                               reserva=reserva,
                               habitacion=habitacion_asignada,
                               mensaje_extra="Se ha realizado un Check-in Temprano. Fechas y precio actualizados.")
    else:
        return render_template('mensaje.html',
                               mensaje=f"No hay disponibilidad para adelantar el Check-in en una habitación {reserva.tipo_habitacion.denominacion}.",
                               url_volver=url_for('cancelar_reserva', id=reserva.id),
                               texto_boton="Cancelar Reserva e Iniciar Walk-in")


@app.route('/admin/walkin_config/<int:persona_id>', methods=['GET', 'POST'])
def admin_walkin_config(persona_id):
    """Paso 1 Walk-in: Elegir fechas y personas"""
    persona_logueada = obtener_persona_logueada()
    cliente = PersonaLogic.get_one_persona(persona_id)
    form = WalkinForm()
    hoy = date.today()

    if request.method == 'POST' and form.validate_on_submit():
        # Buscar tipos disponibles para HOY
        f_egreso = form.fecha_egreso.data
        cant_pax = form.cantidad_personas.data

        if f_egreso <= hoy:
            return render_template('admin_walkin_config.html', form=form, cliente=cliente, hoy=hoy,
                                   error="La salida debe ser posterior a hoy.")

        # Usamos la lógica de búsqueda existente
        ideales, otros = TipoHabitacionLogic.buscar_tipos_disponibles(hoy, f_egreso, cant_pax)

        # Unimos listas para simplificar selección de admin
        todos_tipos = ideales + otros

        return render_template('admin_walkin_select.html',
                               persona_logueada=persona_logueada,
                               cliente=cliente,
                               tipos=todos_tipos,
                               fecha_ingreso=hoy,
                               fecha_egreso=f_egreso,
                               cant_pax=cant_pax)

    return render_template('admin_walkin_config.html',
                           form=form, cliente=cliente, hoy=hoy, persona_logueada=persona_logueada)


@app.route('/admin/walkin_confirmar', methods=['POST'])
def admin_walkin_confirmar():
    persona_logueada = obtener_persona_logueada()
    cliente_id = request.form['cliente_id']
    tipo_id = request.form['tipo_id']
    fecha_ingreso = datetime.strptime(request.form['fecha_ingreso'], '%Y-%m-%d').date()
    fecha_egreso = datetime.strptime(request.form['fecha_egreso'], '%Y-%m-%d').date()
    cant_pax = int(request.form['cant_pax'])
    precio_total = float(request.form['precio_total'])
    habitacion = HabitacionLogic.get_habitacion_disponible_by_tipo(tipo_id, fecha_ingreso, fecha_egreso)
    if not habitacion:
        return render_template('mensaje.html', mensaje="Error: La habitación ya no está disponible.")
    from entity_models.estadia_model import Estadia
    from data.data_estadia import DataEstadia
    nueva_estadia = Estadia(
        persona_id=cliente_id,
        tipo_habitacion_id=tipo_id,
        habitacion_id=habitacion.id,
        fecha_ingreso=fecha_ingreso,
        fecha_egreso=fecha_egreso,
        precio_total=precio_total,
        cantidad_personas=cant_pax,
        estado='En curso'  # Walk-in es inmediato
    )
    DataEstadia.add_estadia(nueva_estadia)
    EmailLogic.enviar_bienvenida_checkin(nueva_estadia)
    return render_template('admin_checkin_exitoso.html',
                           persona_logueada=persona_logueada,
                           reserva=nueva_estadia,
                           habitacion=habitacion,
                           mensaje_extra="Walk-in registrado exitosamente.")


@app.route('/admin/procesar_checkin/<int:reserva_id>')
def admin_procesar_checkin(reserva_id):
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return redirect(url_for('login'))
    try:
        reserva = EstadiaLogic.get_one_estadia(reserva_id)
        if reserva.fecha_ingreso != date.today():
            return render_template('mensaje.html',
                                   mensaje="El Check-in solo se puede realizar en la fecha de ingreso estipulada.")
        habitacion_asignada = HabitacionLogic.get_habitacion_disponible_by_tipo(
            reserva.tipo_habitacion_id,
            reserva.fecha_ingreso,
            reserva.fecha_egreso
        )
        if not habitacion_asignada:
            return render_template('mensaje.html',
                                   mensaje='Error: No hay habitaciones físicas disponibles para asignar en este momento.')
        reserva.estado = 'En curso'
        reserva.habitacion_id = habitacion_asignada.id

        from data.data_estadia import DataEstadia
        DataEstadia.update_estadia()
        EmailLogic.enviar_bienvenida_checkin(reserva)
        return render_template('admin_checkin_exitoso.html',
                               persona_logueada=persona_logueada,
                               reserva=reserva,
                               habitacion=habitacion_asignada)
    except Exception as e:
        app.logger.error(f"Error en checkin: {e}")
        return render_template('mensaje.html', mensaje="Error al procesar el Check-in")

@app.route('/admin/cargar_servicios', methods=['GET', 'POST'])
def admin_cargar_servicios():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return redirect(url_for('login'))
    form = CargarConsumoForm()
    estadias_activas = Estadia.query.filter_by(estado='En curso').all()
    opciones_estadias = []
    for e in estadias_activas:
        nro_hab = e.habitacion.nro_habitacion if e.habitacion else 'S/A'
        label = f"Hab {nro_hab} - {e.persona.apellido}, {e.persona.nombre}"
        opciones_estadias.append((e.id, label))
    form.estadia_id.choices = opciones_estadias
    servicios = ServicioLogic.get_all_servicios()
    form.servicio_id.choices = [(s.id, f"{s.descripcion} (${s.precio})") for s in servicios]
    if request.method == 'POST' and form.validate_on_submit():
        try:
            ServicioLogic.registrar_consumo(
                estadia_id=form.estadia_id.data,
                servicio_id=form.servicio_id.data,
                cantidad=form.cantidad.data
            )
            return render_template('mensaje.html',
                                   mensaje="Consumo registrado exitosamente",
                                   url_volver=url_for('home'),
                                   texto_boton="Volver al Menú Principal")
        except Exception as e:
            app.logger.error(f"Error al cargar consumo: {e}")
            return render_template('mensaje.html', mensaje="Error al registrar el consumo.")
    if not estadias_activas:
        return render_template('mensaje.html',
                               mensaje="No hay habitaciones ocupadas (Check-in realizado) para cargar servicios.")
    return render_template('admin_add_servicios.html',
                           form=form,
                           persona_logueada=persona_logueada)

@app.route('/mis_consumos/<int:estadia_id>')
def mis_consumos(estadia_id):
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada:
        return redirect(url_for('login'))
    estadia = EstadiaLogic.get_one_estadia(estadia_id)
    if estadia.persona_id != persona_logueada.id:
        return render_template('mensaje.html', mensaje="Acceso denegado")
    consumos = estadia.consumos
    total_consumos = sum(c.cantidad * c.precio_unitario_historico for c in consumos)
    return render_template('mis_consumos.html',
                           persona_logueada=persona_logueada,
                           estadia=estadia,
                           consumos=consumos,
                           total=total_consumos)

@app.route('/admin/checkout')
def admin_checkout_list():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return render_template('mensaje.html', mensaje='Acceso denegado')
    from entity_models.estadia_model import Estadia
    estadias = Estadia.query.filter_by(estado='En curso').order_by(Estadia.fecha_egreso).all()
    hoy = date.today()
    return render_template('admin_checkout_list.html',
                           persona_logueada=persona_logueada,
                           estadias=estadias,
                           hoy=hoy)


@app.route('/admin/procesar_checkout/<int:estadia_id>', methods=['GET', 'POST'])
def admin_procesar_checkout(estadia_id):
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return redirect(url_for('login'))
    estadia = EstadiaLogic.get_one_estadia(estadia_id)
    total_consumos = sum(c.cantidad * c.precio_unitario_historico for c in estadia.consumos)
    total_a_cobrar = total_consumos
    if request.method == 'POST':
        exito, mensaje = EstadiaLogic.realizar_checkout(estadia_id)
        if exito:
            EmailLogic.enviar_recibo_checkout(estadia, total_consumos, total_a_cobrar)
            return render_template('mensaje.html',
                                   mensaje="Check-out realizado correctamente. Habitación liberada.",
                                   url_volver=url_for('home'),
                                   texto_boton="Volver al Menú Principal")
        else:
            return render_template('mensaje.html', mensaje=mensaje)

    return render_template('admin_checkout_process.html',
                           persona_logueada=persona_logueada,
                           estadia=estadia,
                           total_consumos=total_consumos,
                           total_a_cobrar=total_a_cobrar)

@app.route('/admin/modificar_estadia/<int:id>', methods=['GET', 'POST'])
def admin_modificar_estadia(id):
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return redirect(url_for('login'))
    estadia = EstadiaLogic.get_one_estadia(id)
    form = ModificarEgresoForm()
    if request.method == 'GET':
        form.fecha_egreso.data = estadia.fecha_egreso

    if request.method == 'POST' and form.validate_on_submit():
        nueva_fecha = form.fecha_egreso.data
        exito, mensaje = EstadiaLogic.modificar_fecha_egreso(id, nueva_fecha)
        if exito:
            return render_template('mensaje.html',
                                   mensaje=f"Estadía actualizada. Nueva salida: {nueva_fecha.strftime('%d/%m/%Y')}",
                                   url_volver=url_for('admin_checkout_list'),
                                   texto_boton="Volver al Listado")
        else:
            return render_template('admin_modificar_estadia.html',
                                   form=form, estadia=estadia, error=mensaje, persona_logueada=persona_logueada)
    return render_template('admin_modificar_estadia.html',
                           form=form, estadia=estadia, persona_logueada=persona_logueada)


@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return redirect(url_for('login'))
    hoy = date.today()
    form_ventas = ReporteVentasForm(prefix='ventas')
    form_ocupacion = ReporteOcupacionForm(prefix='ocupacion')
    form_ocupacion.anio.choices = [(hoy.year, hoy.year), (hoy.year - 1, hoy.year - 1)]
    if request.method == 'GET':
        primer_dia_mes = date(hoy.year, hoy.month, 1)
        ultimo_dia_mes = date(hoy.year, hoy.month, calendar.monthrange(hoy.year, hoy.month)[1])
        form_ventas.fecha_desde.data = primer_dia_mes
        form_ventas.fecha_hasta.data = ultimo_dia_mes
        form_ocupacion.anio.data = hoy.year

    # Lógica de Ventas
    if form_ventas.submit.data and form_ventas.validate():
        f_desde = form_ventas.fecha_desde.data
        f_hasta = form_ventas.fecha_hasta.data
    else:
        f_desde = form_ventas.fecha_desde.data
        f_hasta = form_ventas.fecha_hasta.data
    ventas_resultados = EstadiaLogic.generar_reporte_ventas(f_desde, f_hasta)
    total_ingresos = 0
    for r in ventas_resultados:
        extra = sum(c.cantidad * c.precio_unitario_historico for c in r.consumos)
        total_ingresos += (r.precio_total + extra)

    # Lógica de Ocupación
    if form_ocupacion.submit.data and form_ocupacion.validate():
        anio_seleccionado = form_ocupacion.anio.data
    else:
        anio_seleccionado = form_ocupacion.anio.data or hoy.year
    ocupacion_data = EstadiaLogic.calcular_ocupacion_mensual(anio_seleccionado)
    return render_template('admin_dashboard.html',
                           persona_logueada=persona_logueada,
                           form_ventas=form_ventas,
                           form_ocupacion=form_ocupacion,
                           ventas=ventas_resultados,
                           total_ingresos=total_ingresos,
                           ocupacion_data=ocupacion_data,
                           anio_ocupacion=anio_seleccionado)


@app.route('/admin/enviar_recordatorios')
def admin_enviar_recordatorios():
    persona_logueada = obtener_persona_logueada()
    if not persona_logueada or persona_logueada.tipo_persona != 'administrador':
        return redirect(url_for('login'))
    manana = date.today() + timedelta(days=1)
    from entity_models.estadia_model import Estadia
    reservas_manana = Estadia.query.filter(
        Estadia.fecha_ingreso == manana,
        Estadia.estado == 'Reservada'
    ).all()
    count = 0
    for r in reservas_manana:
        EmailLogic.enviar_recordatorio_manana(r)
        count += 1
    return render_template('mensaje.html',
                           mensaje=f"Se han enviado {count} recordatorios para las reservas de mañana ({manana.strftime('%d/%m')}).",
                           persona_logueada=persona_logueada,
                           url_volver=url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)