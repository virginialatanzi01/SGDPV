from data.database import Database

db = Database.db

class Servicio(db.Model):
    __tablename__ = 'servicio'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    precio = db.Column(db.Float, nullable=False)

    consumos = db.relationship('Consumo', backref='servicio', lazy=True)