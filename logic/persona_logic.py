from sqlite3 import IntegrityError

import sqlalchemy
from flask import Flask
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.orm.exc import ObjectDeletedError, StaleDataError, FlushError
from werkzeug.exceptions import NotFound

from data.data_persona import DataPersona
from entity_models.persona_model import Persona
app = Flask(__name__)

class PersonaLogic:
    @classmethod
    def get_all_personas(cls):
        try:
            personas = DataPersona.get_all_personas()
            return list(personas)
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_all_administradores(cls):
        try:
            administradores = DataPersona.get_all_administradores()
            return list(administradores)
        except SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_all_clientes(cls):
        try:
            clientes = DataPersona.get_all_clientes()
            return clientes
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_one_persona(cls, id):
        try:
            persona = DataPersona.get_one_persona(id)
            return persona
        except NotFound as e:
            app.logger.debug(f'Persona no encontrada: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def add_persona(cls, persona, contrasena):
        try:
            DataPersona.add_persona(persona, contrasena)
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.debug(f'Error en la base de datos: {e}')
            raise e
        except Exception as e:
            app.logger.debug(f'Error inesperado: {e}')
            raise e

    @classmethod
    def get_persona_by_user(cls, username):
        try:
            persona = DataPersona.get_persona_by_user(username)
            if persona is not None:
                return persona
            else:
                return None
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.debug(f"Error de base de datos: {e}")
            raise e
        except Exception as e:
            app.logger.debug(f"Error inesperado: {e}")
            raise e

    @classmethod
    def valida_credenciales(cls, username, contrasena):
        try:
            persona = PersonaLogic.get_persona_by_user(username)
            if persona:
                persona_validada = Persona.valida_contrasena(persona, contrasena)
                print(f'Valor booleano: {persona_validada}')
                if persona_validada:
                    return persona
                else:
                    return None
            return None
        except sqlalchemy.exc.SQLAlchemyError as e:
            app.logger.debug(f"Error de base de datos: {e}")
            raise e
        except Exception as e:
            app.logger.debug(f"Error inesperado: {e}")
            raise e

    @classmethod
    def delete_persona(cls, id):
        try:
            DataPersona.delete_persona(id)
        except IntegrityError as e:
            raise e
        except ObjectDeletedError as e:
            raise e
        except StaleDataError as e:
            raise e

    @classmethod
    def update_persona(cls, persona, contrasena):
        try:
            DataPersona.update_persona(persona, contrasena)
        except IntegrityError as e:
            raise e
        except StaleDataError as e:
            raise e
        except FlushError as e:
            raise e
        except DBAPIError as e:
            raise e

    @classmethod
    def get_persona_by_email(cls, email):
        return DataPersona.get_persona_by_email(email)