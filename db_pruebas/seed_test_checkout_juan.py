import sys
import os
from datetime import date, timedelta

# Configuración de path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from data.database import Database
from entity_models.estadia_model import Estadia
from entity_models.persona_model import Persona
from entity_models.habitacion_model import Habitacion
from entity_models.tipo_habitacion_model import TipoHabitacion


def cargar_checkout_virgi():
    with app.app_context():
        print("--- Creando estadía 'En curso' para Virgi (Check-out HOY) ---")

        # 1. Buscar o Crear tu Usuario
        dni_virgi = '43610230'
        email_virgi = 'mvirginialatanzi@gmail.com'

        usuario = Persona.query.filter_by(nro_documento=dni_virgi).first()

        if not usuario:
            print("Creando usuario Virgi Latanzi...")
            usuario = Persona()
            usuario.nombre = "Virginia"
            usuario.apellido = "Latanzi"
            usuario.tipo_documento = "DNI"
            usuario.nro_documento = dni_virgi
            usuario.fecha_nacimiento = date(1995, 1, 1)
            usuario.email = email_virgi
            usuario.telefono = "111222333"
            usuario.nombre_usuario = "virgi.latanzi"
            usuario.tipo_persona = "cliente"
            usuario.establece_contrasena("1234")
            Database.db.session.add(usuario)
            Database.db.session.commit()
        else:
            # Aseguramos que tenga el email correcto
            usuario.email = email_virgi
            Database.db.session.commit()

        print(f"Cliente: {usuario.apellido} (Email: {usuario.email})")

        # 2. Buscar Habitación Disponible (ej: 104)
        habitacion = Habitacion.query.filter_by(nro_habitacion='104').first()
        if not habitacion:
            habitacion = Habitacion.query.first()

        tipo = TipoHabitacion.query.get(habitacion.tipo_id)

        # 3. Fechas: Ayer -> Hoy
        hoy = date.today()
        ayer = hoy - timedelta(days=1)

        # 4. Crear Estadía
        estadia = Estadia(
            fecha_ingreso=ayer,
            fecha_egreso=hoy,
            estado='En curso',  # Estado listo para salir
            precio_total=tipo.precio_por_noche,
            cantidad_personas=1,
            persona_id=usuario.id,
            tipo_habitacion_id=tipo.id,
            habitacion_id=habitacion.id
        )

        try:
            Database.db.session.add(estadia)
            Database.db.session.commit()
            print(f"✅ Estadía creada. Ve a 'Check-out' y procesa la salida de la Hab #{habitacion.nro_habitacion}.")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == '__main__':
    cargar_checkout_virgi()