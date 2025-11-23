from data.database import Database

db = Database.db

class TipoHabitacion(db.Model):
    __tablename__ = 'tipo_habitacion'
    id = db.Column(db.Integer, primary_key=True)
    denominacion = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    capacidad_personas = db.Column(db.Integer, nullable=False)
    precio_por_noche = db.Column(db.Float, nullable=False)
    nombre_imagen = db.Column(db.String(100))

    # Relación con habitaciones físicas
    habitaciones = db.relationship('Habitacion', backref='tipo_habitacion', lazy=True)