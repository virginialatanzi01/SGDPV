from data.database import Database
from entity_models.tipo_habitacion_model import TipoHabitacion
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app as app

class DataTipoHabitacion:
    @classmethod
    def get_all_tipos(cls):
        try:
            return TipoHabitacion.query.all()
        except SQLAlchemyError as e:
            app.logger.error(f"Error en base de datos: {e}")
            raise e
        except Exception as e:
            app.logger.error(f"Error inesperado: {e}")
            raise e

    @classmethod
    def get_one_tipo(cls, id):
        try:
            return TipoHabitacion.query.get_or_404(id)
        except SQLAlchemyError as e:
            app.logger.error(f"Error en base de datos: {e}")
            raise e
        except Exception as e:
            app.logger.error(f"Error inesperado: {e}")
            raise e

    @classmethod
    def get_tipos_by_capacidad(cls, capacidad_minima):
        try:
            tipos = TipoHabitacion.query.filter(TipoHabitacion.capacidad_personas >= capacidad_minima).all()
            return tipos
        except SQLAlchemyError as e:
            app.logger.error(f"Error en base de datos: {e}")
            raise e
        except Exception as e:
            app.logger.error(f"Error inesperado: {e}")
            raise e