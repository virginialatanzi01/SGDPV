import sys
import os
import random
from datetime import date, timedelta

# Configurar path para importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from data.database import Database
from entity_models.persona_model import Persona
from entity_models.habitacion_model import Habitacion
from entity_models.tipo_habitacion_model import TipoHabitacion
from entity_models.estadia_model import Estadia
from entity_models.servicio_model import Servicio
from entity_models.consumo_model import Consumo


def cargar_datos_dashboard():
    with app.app_context():
        print("🚀 Iniciando carga masiva para el Dashboard...")

        # 1. Crear Clientes Ficticios
        clientes = []
        print("--- Creando Clientes Random ---")
        for i in range(1, 15):  # 14 clientes nuevos
            dni = f"990000{i:02d}"  # Genera DNI tipo 99000001, 99000002...
            existe = Persona.query.filter_by(nro_documento=dni).first()

            if not existe:
                p = Persona()
                p.nombre = f"Cliente {i}"
                p.apellido = "Test"
                p.tipo_documento = "DNI"
                p.nro_documento = dni
                p.email = f"cliente{i}@test.com"
                p.nombre_usuario = f"cliente{i}"
                p.tipo_persona = "cliente"
                p.establece_contrasena("1234")
                Database.db.session.add(p)
                clientes.append(p)
            else:
                clientes.append(existe)

        Database.db.session.commit()

        # 2. Obtener recursos existentes
        habitaciones = Habitacion.query.all()
        servicios = Servicio.query.all()
        tipos = {t.id: t for t in TipoHabitacion.query.all()}  # Diccionario para acceso rápido

        if not habitaciones:
            print("❌ Error: Faltan habitaciones. Ejecuta seed_alojamientos.py primero.")
            return

        # 3. Generar Estadías (Año actual y anterior)
        anio_actual = date.today().year
        anios = [anio_actual, anio_actual - 1]


        cantidad_estadias = 80  # Generamos 80 reservas para tener buen volumen
        estadias_creadas = 0

        for _ in range(cantidad_estadias):
            # Elegir datos al azar
            cliente = random.choice(clientes)
            habitacion = random.choice(habitaciones)
            tipo = tipos[habitacion.tipo_id]
            anio = random.choice(anios)
            mes = random.randint(1, 12)

            # Evitar errores de fecha (ej: 30 de febrero)
            try:
                dia = random.randint(1, 28)
                fecha_ingreso = date(anio, mes, dia)
            except:
                continue  # Si falla la fecha, saltamos esta iteración

            noches = random.randint(1, 7)  # Estadías de 1 a 7 noches
            fecha_egreso = fecha_ingreso + timedelta(days=noches)

            # Calcular precio
            precio_base = tipo.precio_por_noche * noches

            # Determinar Estado
            estado = 'Finalizada'  # Por defecto histórica

            # Si la fecha es futura, es una reserva pendiente
            if fecha_ingreso > date.today():
                estado = 'Reservada'
                habitacion_id = None  # Aún no asignada
            # Si la fecha abarca HOY, está en curso
            elif fecha_ingreso <= date.today() and fecha_egreso >= date.today():
                estado = 'En curso'
                habitacion_id = habitacion.id
            else:
                # Pasada y finalizada
                estado = 'Finalizada'
                habitacion_id = habitacion.id

            nueva_estadia = Estadia(
                fecha_ingreso=fecha_ingreso,
                fecha_egreso=fecha_egreso,
                estado=estado,
                precio_total=precio_base,
                cantidad_personas=random.randint(1, tipo.capacidad_personas),
                persona_id=cliente.id,
                tipo_habitacion_id=tipo.id,
                habitacion_id=habitacion_id
            )

            Database.db.session.add(nueva_estadia)
            Database.db.session.commit()  # Guardar para tener ID y cargar consumos
            estadias_creadas += 1

            # 4. Generar Consumos (Solo si está finalizada o en curso)
            if estado in ['Finalizada', 'En curso'] and servicios:
                # 60% de probabilidad de tener consumos extra
                if random.random() > 0.4:
                    cant_items = random.randint(1, 5)
                    for _ in range(cant_items):
                        srv = random.choice(servicios)
                        consumo = Consumo(
                            estadia_id=nueva_estadia.id,
                            servicio_id=srv.id,
                            cantidad=random.randint(1, 3),
                            precio_unitario_historico=srv.precio,
                            # Fecha de consumo aleatoria dentro de la estadía
                            fecha_consumo=fecha_ingreso + timedelta(days=random.randint(0, noches - 1))
                        )
                        Database.db.session.add(consumo)

        Database.db.session.commit()

if __name__ == '__main__':
    cargar_datos_dashboard()