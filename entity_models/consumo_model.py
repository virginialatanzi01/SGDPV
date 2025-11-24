from data.database import Database
from datetime import date

db = Database.db

class Consumo(db.Model):
    __tablename__ = 'consumo'
    id = db.Column(db.Integer, primary_key=True)
    estadia_id = db.Column(db.Integer, db.ForeignKey('estadia.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicio.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_consumo = db.Column(db.Date, default=date.today)

    precio_unitario_historico = db.Column(db.Float, nullable=False)