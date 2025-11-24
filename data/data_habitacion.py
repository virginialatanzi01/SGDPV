from data.database import Database
from entity_models.habitacion_model import Habitacion
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app as app

class DataHabitacion:
    @classmethod
    def get_habitaciones_by_tipo(cls, tipo_id):
        try:
            return Habitacion.query.filter_by(tipo_id=tipo_id).order_by(Habitacion.nro_habitacion).all()
        except SQLAlchemyError as e:
            app.logger.error(f"Error al obtener habitaciones por tipo: {e}")
            raise e

    @classmethod
    def get_habitacion_by_id(cls, id):
        try:
            return Habitacion.query.get_or_404(id)
        except SQLAlchemyError as e:
            app.logger.error(f"Error al obtener habitación por ID: {e}")
            raise e