import sqlalchemy
from flask import Flask
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DBAPIError
from sqlalchemy.orm.exc import ObjectDeletedError, StaleDataError, FlushError
from werkzeug.exceptions import NotFound

from data.database import Database
from entity_models.persona_model import Persona

app = Flask(__name__)

class DataPersona:
    @classmethod
    def get_all_personas(cls):
        try:
            personas = Persona.query.order_by('id')
            return personas
        except SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_all_administradores(cls):
        try:
            administradores = Persona.query.filter_by(tipo_persona='administrador').order_by('id')
            return administradores
        except SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_all_clientes(cls):
        try:
            clientes = Persona.query.filter_by(tipo_persona='cliente').order_by(Persona.id)
            return clientes
        except SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def add_persona(cls, persona, contrasena):
        try:
            persona.establece_contrasena(contrasena)
            Database.db.session.add(persona)
            Database.db.session.commit()
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_one_persona(cls, id):
        try:
            persona = Persona.query.get_or_404(id)
            return persona
        except NotFound as e:
            app.logger.debug(f'Persona no encontrada: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_persona_by_user(cls, username):
        try:
            persona = Persona.query.filter_by(nombre_usuario=username).first()
            return persona
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.debug(f"Error de base de datos: {e}")
            raise e
        except Exception as e:
            app.logger.debug(f"Error inesperado: {e}")
            raise e

    @classmethod
    def delete_persona(cls, id):
        try:
            persona = DataPersona.get_one_persona(id)
            Database.db.session.delete(persona)
            Database.db.session.commit()
        except IntegrityError as e:
            raise e
        except ObjectDeletedError as e:
            raise e
        except StaleDataError as e:
            raise e

    @classmethod
    def update_persona(cls, persona, contrasena):
        try:
            if contrasena:
                persona.establece_contrasena(contrasena)
            Database.db.session.add(persona)
            Database.db.session.commit()
        except IntegrityError as e:
            raise e
        except StaleDataError as e:
            raise e
        except FlushError as e:
            raise e
        except DBAPIError as e:
            raise e

    @classmethod
    def get_one_persona(cls, id):
        try:
            persona = Persona.query.get_or_404(id)
            return persona
        except NotFound as e:
            app.logger.debug(f'Persona no encontrada: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_persona_by_email(cls, email):
        try:
            return Persona.query.filter_by(email=email).first()
        except Exception as e:
            return None