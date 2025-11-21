from flask import Flask
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound

from data.database import Database
from entity_models.habitacion_model import Habitacion
app = Flask(__name__)

class DataHabitacion:
    @classmethod
    def get_all_habitaciones(cls):
        try:
            return Habitacion.query.order_by('nro_habitacion').all()
        except SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e

    @classmethod
    def get_one_habitacion(cls, nro_habitacion):
        try:
            habitacion = Habitacion.query.get_or_404(nro_habitacion)
            return habitacion
        except SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except NotFound:
            app.logger.debug(f'Habitación no encontrada')
            raise NotFound(description='Habitación no encontrada')

    @classmethod
    def add_habitacion(cls, habitacion):
        try:
            Database.db.session.add(habitacion)
            Database.db.session.commit()
        except SQLAlchemyError as e:
            Database.db.session.rollback()
            app.logger.debug(f'Error al agregar la habitación: {e}')
            raise e

    @classmethod
    def delete_habitacion(cls, nro_habitacion):
        try:
            habitacion = cls.get_one_habitacion(nro_habitacion)
            Database.db.session.delete(habitacion)
            Database.db.session.commit()
        except SQLAlchemyError as e:
            Database.db.session.rollback()
            app.logger.debug(f'Error al eliminar la habitación: {e}')
            raise e
        except NotFound:
            app.logger.debug('Habitación no encontrada')
            raise NotFound(description='Habitación no encontrada')