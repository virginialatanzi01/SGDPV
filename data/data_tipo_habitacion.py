from flask import Flask
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import NotFound

from data.database import Database
from entity_models.tipo_habitacion_model import TipoHabitacion
app = Flask(__name__)

class DataTipoHabitacion:
    @classmethod
    def get_all_tipos(cls):
        try:
            tipo_habitacion = TipoHabitacion.query.order_by('id').all()
            return tipo_habitacion
        except SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_one_tipo(cls, id):
        try:
            tipo_habitacion = TipoHabitacion.query.get_or_404(id)
            return tipo_habitacion
        except SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except NotFound:
            app.logger.debug('Tipo de habitación no encontrada')
            raise NotFound(description='Tipo de habitación no encontrada')

    @classmethod
    def get_tipo_by_den(cls, denominacion):
        try:
            tipo = TipoHabitacion.query.filter_by(denominacion=denominacion).first()
            return tipo
        except SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def add_tipo(cls, tipo):
        try:
            Database.db.session.add(tipo)
            Database.db.session.commit()
        except SQLAlchemyError as e:
            app.logger.debug(f'Error al agregar el tipo de habitacion: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def delete_tipo(cls, id):
        try:
            tipo = cls.get_one_tipo(id)
            Database.db.session.delete(tipo)
            Database.db.session.commit()
        except SQLAlchemyError as e:
            app.logger.debug(f'Error al eliminar el tipo de habitación: {e}')
            raise e
        except NotFound:
            app.logger.debug('Tipo de habitación no encontrada')
            raise NotFound(description='Tipo de habitación no encontrada')
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e