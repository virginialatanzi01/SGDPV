from data.database import Database
db = Database.db

class Habitacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nro_habitacion = db.Column(db.String(10), unique=True, nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo_habitacion.id'), nullable=False)
    def to_dict(self):
        return {
            "id": self.id,
            "nro_habitacion": self.nro_habitacion,
            "tipo_id": self.tipo_id,
        }
    @classmethod
    def from_dict(cls, data):
        return cls(
            nro_habitacion=data.get("nro_habitacion"),
            tipo_id=data.get("tipo_id"),
        )