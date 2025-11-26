import sys
import os
from datetime import date, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from data.database import Database
from entity_models.estadia_model import Estadia
from entity_models.persona_model import Persona
from entity_models.tipo_habitacion_model import TipoHabitacion


def cargar_recordatorio_virgi():
    with app.app_context():
        print("--- Creando reserva para MAÑANA (Test Email Recordatorio) ---")

        # 1. Buscar tu Usuario
        dni_virgi = '43610230'
        email_virgi = 'mvirginialatanzi@gmail.com'
        usuario = Persona.query.filter_by(nro_documento=dni_virgi).first()

        if not usuario:
            print(f"❌ Error: Primero ejecuta el script de checkout o crea el usuario {dni_virgi}.")
            return

        # Asegurar email correcto
        if usuario.email != email_virgi:
            usuario.email = email_virgi
            Database.db.session.commit()

        # 2. Tipo Habitación
        tipo = TipoHabitacion.query.first()

        # 3. Fechas: Mañana -> Pasado mañana
        manana = date.today() + timedelta(days=1)
        salida = manana + timedelta(days=2)

        # 4. Crear Reserva
        reserva = Estadia(
            fecha_ingreso=manana,
            fecha_egreso=salida,
            estado='Reservada',  # Estado pendiente
            precio_total=tipo.precio_por_noche * 2,
            cantidad_personas=2,
            persona_id=usuario.id,
            tipo_habitacion_id=tipo.id,
            habitacion_id=None
        )

        try:
            Database.db.session.add(reserva)
            Database.db.session.commit()
            print(f"✅ Reserva creada para MAÑANA ({manana}).")
            print("👉 Ve al menú Admin > 'Enviar recordatorios' y deberías recibir el correo.")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    cargar_recordatorio_virgi()