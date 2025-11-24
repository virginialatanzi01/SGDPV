import sys
import os
from datetime import date, timedelta

# Agregamos el directorio padre al path para poder importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from data.database import Database
from entity_models.estadia_model import Estadia
from entity_models.persona_model import Persona
from entity_models.habitacion_model import Habitacion
from entity_models.tipo_habitacion_model import TipoHabitacion
from entity_models.servicio_model import Servicio
from entity_models.consumo_model import Consumo


def cargar_estadia_con_consumos():
    with app.app_context():
        print("--- Generando estadía con CONSUMOS para Check-out HOY ---")

        # 1. Fechas: Anteayer -> Hoy (2 noches)
        hoy = date.today()
        ingreso = hoy - timedelta(days=2)

        # 2. Cliente (Buscamos uno existente)
        cliente = Persona.query.filter_by(tipo_persona='cliente').first()
        if not cliente:
            print("❌ Error: No hay clientes cargados.")
            return

        # 3. Habitación (Cualquiera disponible o la 102 para variar)
        habitacion = Habitacion.query.filter_by(nro_habitacion='102').first()
        if not habitacion:
            habitacion = Habitacion.query.first()

        tipo = TipoHabitacion.query.get(habitacion.tipo_id)

        # 4. Crear Estadía 'En curso'
        print(f"Creando estadía para {cliente.nombre} en Hab {habitacion.nro_habitacion}...")

        nueva_estadia = Estadia(
            fecha_ingreso=ingreso,
            fecha_egreso=hoy,
            estado='En curso',
            precio_total=tipo.precio_por_noche * 2,  # 2 noches
            cantidad_personas=2,
            persona_id=cliente.id,
            tipo_habitacion_id=tipo.id,
            habitacion_id=habitacion.id
        )

        Database.db.session.add(nueva_estadia)
        Database.db.session.commit()  # Guardamos para tener el ID de estadía

        # 5. Cargar Consumos de prueba
        # Buscamos servicios comunes
        serv_almuerzo = Servicio.query.filter(Servicio.descripcion.ilike('%Almuerzo%')).first()
        serv_lavanderia = Servicio.query.filter(Servicio.descripcion.ilike('%lavandería%')).first()

        consumos_creados = 0

        if serv_almuerzo:
            consumo1 = Consumo(
                estadia_id=nueva_estadia.id,
                servicio_id=serv_almuerzo.id,
                cantidad=2,  # 2 Platos
                precio_unitario_historico=serv_almuerzo.precio,
                fecha_consumo=ingreso  # Consumido el día que llegó
            )
            Database.db.session.add(consumo1)
            consumos_creados += 1

        if serv_lavanderia:
            consumo2 = Consumo(
                estadia_id=nueva_estadia.id,
                servicio_id=serv_lavanderia.id,
                cantidad=1,
                precio_unitario_historico=serv_lavanderia.precio,
                fecha_consumo=hoy  # Consumido hoy antes de irse
            )
            Database.db.session.add(consumo2)
            consumos_creados += 1

        Database.db.session.commit()
        print(f"✅ Estadía creada (ID: {nueva_estadia.id}) finaliza HOY.")
        print(f"✅ Se agregaron {consumos_creados} registros de consumo.")
        print("👉 Ve a 'Check-out' en el menú de Admin para probar el cobro.")


if __name__ == '__main__':
    cargar_estadia_con_consumos()