from data.database import Database
from app import app  # Asegúrate de importar tu instancia de Flask
from entity_models.habitacion_model import Habitacion
from entity_models.tipo_habitacion_model import TipoHabitacion

# Ejecutar dentro del contexto de la aplicación Flask
with app.app_context():
    Database.db.create_all()
    print("Tablas creadas correctamente.")