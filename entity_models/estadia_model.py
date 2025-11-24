from data.database import Database

db = Database.db

class Estadia(db.Model):
    __tablename__ = 'estadia'
    id = db.Column(db.Integer, primary_key=True)
    fecha_ingreso = db.Column(db.Date, nullable=False)
    fecha_egreso = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(50), nullable=False)  # 'Reservada', 'En curso', 'Finalizada', 'Cancelada'
    precio_total = db.Column(db.Float, nullable=False)

    persona_id = db.Column(db.Integer, db.ForeignKey('persona.id'), nullable=False)
    tipo_habitacion_id = db.Column(db.Integer, db.ForeignKey('tipo_habitacion.id'), nullable=False)
    # La habitación física se asigna en el Check-in (nullable=True por ahora)
    habitacion_id = db.Column(db.Integer, db.ForeignKey('habitacion.id'), nullable=True)

    persona = db.relationship('Persona', backref='estadias')
    tipo_habitacion = db.relationship('TipoHabitacion', backref='estadias')
    habitacion = db.relationship('Habitacion', backref='estadias')