import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from data.database import Database
from entity_models.servicio_model import Servicio

def cargar_servicios():
    with app.app_context():
        servicios = [
            {"descripcion": "Room service: Café + medialunas", "precio": 5000},
            {"descripcion": "Almuerzo o cena: Plato del día", "precio": 10000},
            {"descripcion": "Cargo por room service", "precio": 4000},
            {"descripcion": "Servicio de lavandería", "precio": 7000},
            {"descripcion": "Transfer desde/hacia terminal", "precio": 10000},
            {"descripcion": "Kit San Valentín", "precio": 25000},
            {"descripcion": "Kit cumpleaños", "precio": 15000}
        ]

        print("Cargando servicios...")
        for data in servicios:
            existe = Servicio.query.filter_by(descripcion=data["descripcion"]).first()
            if not existe:
                nuevo = Servicio(descripcion=data["descripcion"], precio=data["precio"])
                Database.db.session.add(nuevo)
                print(f" + Agregado: {data['descripcion']}")
            else:
                print(f" - Ya existe: {data['descripcion']}")

        Database.db.session.commit()

if __name__ == '__main__':
    cargar_servicios()