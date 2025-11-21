from data.database import Database

db = Database.db

class TipoHabitacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    denominacion = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    foto = db.Column(db.String(255))  # Ruta o URL de la imagen
    capacidad_personas = db.Column(db.Integer, nullable=False)
    precio_por_dia = db.Column(db.Float, nullable=False)

    habitaciones = db.relationship("Habitacion", backref="tipo", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "denominacion": self.denominacion,
            "descripcion": self.descripcion,
            "foto": self.foto,
            "capacidad_personas": self.capacidad_personas,
            "precio_por_dia": self.precio_por_dia,
            "habitaciones": [habitacion.to_dict() for habitacion in self.habitaciones]
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            denominacion=data.get("denominacion"),
            descripcion=data.get("descripcion"),
            foto=data.get("foto"),
            capacidad_personas=data.get("capacidad_personas"),
            precio_por_dia=data.get("precio_por_dia"),
        )

# Importamos Habitacion al final para evitar referencia circular
from entity_models.habitacion_model import Habitacion
