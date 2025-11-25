import sys
import os
from datetime import date, timedelta

# Agregamos el directorio padre al path para poder importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from data.database import Database
from entity_models.estadia_model import Estadia
from entity_models.persona_model import Persona
from entity_models.tipo_habitacion_model import TipoHabitacion


def cargar_reserva_no_show():
    with app.app_context():
        print("--- Generando reserva vencida (No-Show) ---")

        # 1. Configurar fechas pasadas
        hoy = date.today()
        hace_dos_dias = hoy - timedelta(days=2)
        salida_futura = hoy + timedelta(days=2)  # Supongamos que se iba a quedar 4 días

        dni_target = '43610230'

        # 2. Buscar Cliente
        cliente = Persona.query.filter_by(nro_documento=dni_target).first()

        # Si no existe el DNI específico, usamos el primero que encuentre para que el script no falle
        if not cliente:
            print(f"⚠️ No se encontró DNI {dni_target}, usando el primer cliente disponible.")
            cliente = Persona.query.filter_by(tipo_persona='cliente').first()

        if not cliente:
            print("❌ Error: No hay clientes en la base de datos.")
            return

        # 3. Obtener un tipo de habitación cualquiera
        tipo = TipoHabitacion.query.first()

        print(f"Generando datos para: {cliente.nombre} {cliente.apellido}")
        print(f"Fecha de Ingreso programada: {hace_dos_dias} (Vencida)")

        # 4. Crear la Reserva Vencida
        reserva_vencida = Estadia(
            fecha_ingreso=hace_dos_dias,
            fecha_egreso=salida_futura,
            estado='Reservada',  # Estado CLAVE: Sigue reservada aunque ya pasó la fecha
            precio_total=tipo.precio_por_noche * 4,
            cantidad_personas=1,
            persona_id=cliente.id,
            tipo_habitacion_id=tipo.id,
            habitacion_id=None  # Sin habitación asignada (nunca hizo check-in)
        )

        try:
            Database.db.session.add(reserva_vencida)
            Database.db.session.commit()
            print(f"✅ Reserva vencida creada (ID: {reserva_vencida.id}).")
            print("👉 PASO A SEGUIR: Ingresa al menú 'Check-in' como Administrador.")
            print("   El sistema debería detectar esta fecha pasada y cancelarla automáticamente.")
        except Exception as e:
            Database.db.session.rollback()
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    cargar_reserva_no_show()