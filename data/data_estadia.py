from data.database import Database
from entity_models.estadia_model import Estadia
from entity_models.habitacion_model import Habitacion
from sqlalchemy import and_

class DataEstadia:
    @classmethod
    def add_estadia(cls, estadia):
        Database.db.session.add(estadia)
        Database.db.session.commit()

    @classmethod
    def get_disponibilidad(cls, tipo_id, f_ingreso, f_egreso):
        total_habitaciones = Habitacion.query.filter_by(tipo_id=tipo_id).count()
        # Contar reservas activas que se solapen con las fechas solicitadas (RN 10)
        reservas_ocupadas = Estadia.query.filter(
            Estadia.tipo_habitacion_id == tipo_id,
            Estadia.estado.in_(['Reservada', 'En curso']),
            and_(Estadia.fecha_ingreso < f_egreso, Estadia.fecha_egreso > f_ingreso)
        ).count()
        return total_habitaciones - reservas_ocupadas