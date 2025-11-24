import sys
import os

# Agregamos el directorio padre al path para poder importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from data.database import Database
# Asegúrate de que el modelo Estadia esté creado como lo definimos antes
from entity_models.estadia_model import Estadia

def limpiar_estadias():
    with app.app_context():
        print("Eliminando todas las reservas de la tabla 'estadia'...")
        try:
            # Borra todos los registros de la tabla Estadia
            num_borrados = Database.db.session.query(Estadia).delete()
            Database.db.session.commit()
            print(f"¡Listo! Se han eliminado {num_borrados} reservas.")
        except Exception as e:
            Database.db.session.rollback()
            print(f"Ocurrió un error: {e}")

if __name__ == '__main__':
    limpiar_estadias()