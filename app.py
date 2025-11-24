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
from entity_models.reserva_form import BusquedaReservaForm, ModificarReservaForm
from entity_models.tipo_habitacion_model import TipoHabitacion
from entity_models.habitacion_model import Habitacion
from entity_models.estadia_model import Estadia
from entity_models.busqueda_cliente_form import BusquedaClienteForm
from entity_models.servicio_model import Servicio
from entity_models.consumo_model import Consumo
from entity_models.consumo_form import CargarConsumoForm

from logic.tipo_habitacion_logic import TipoHabitacionLogic
from logic.persona_logic import PersonaLogic
from logic.persona_logic import PersonaLogic
from logic.estadia_logic import EstadiaLogic
from logic.habitacion_logic import HabitacionLogic
from logic.servicio_logic import ServicioLogic
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
    form = BusquedaClienteForm()
    reservas = None
    dni_buscado = None
    hoy = date.today()
    if request.method == 'POST' and form.validate_on_submit():
        dni_buscado = form.nro_documento.data
        reservas = EstadiaLogic.buscar_reservas_por_dni(dni_buscado)
    return render_template('admin_checkin_buscar.html',
                           persona_logueada=persona_logueada,
                           form=form,
                           reservas=reservas,
                           dni_buscado=dni_buscado,
                           hoy=hoy)

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
        # Aquí se simularía el cobro
        from data.data_estadia import DataEstadia
        DataEstadia.update_estadia()
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

if __name__ == '__main__':
    app.run(debug=True)