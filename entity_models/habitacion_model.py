from data.database import Database
db = Database.db

class Habitacion(db.Model):
    __tablename__ = 'habitacion'
    id = db.Column(db.Integer, primary_key=True)
    nro_habitacion = db.Column(db.String(10), unique=True, nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo_habitacion.id'), nullable=False)