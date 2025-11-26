import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Variables de entorno
load_dotenv()

class Database:
    db = SQLAlchemy()

    @classmethod
    def configura_conexion(cls) -> str:
        user_db = os.getenv('DB_USER')
        pass_db = os.getenv('DB_PASS')
        host_db = os.getenv('DB_HOST')
        port_db = os.getenv('DB_PORT')
        name_db = os.getenv('DB_NAME')

        full_url_db = f'postgresql://{user_db}:{pass_db}@{host_db}:{port_db}/{name_db}'
        return full_url_db