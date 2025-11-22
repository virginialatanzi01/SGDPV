from app import app
from data.database import Database
# Importa todos tus modelos para que SQLAlchemy los reconozca al crear las tablas
from entity_models.persona_model import Persona
from entity_models.tipo_habitacion_model import TipoHabitacion
from entity_models.habitacion_model import Habitacion

# Importa Estadia si ya creaste el archivo, sino coméntalo
# from entity_models.estadia_model import Estadia

with app.app_context():
    # Esto borra TODAS las tablas y datos (Cuidado: es irreversible)
    Database.db.drop_all()
    print("Tablas eliminadas.")

    # Esto crea las tablas de nuevo basadas en tus modelos actuales
    Database.db.create_all()
    print("Tablas creadas nuevamente desde cero.")