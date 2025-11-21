from flask_sqlalchemy import SQLAlchemy

class Database:
    # Inicialización la conexión a la base de datos con SQLAlchemy.
    db = SQLAlchemy()

    @classmethod
    def configura_conexion(cls) -> str:
        # Configuro la conexión a la base de datos
        user_db = 'postgres'
        pass_db = 'cUeNtaPosTgrE2023---'
        host_db = 'localhost'
        port_db = '5432'
        name_db = 'konigari'

        # Creo la cadena de conexión completa a la base de datos(PostgreSQL en nuestro caso)
        full_url_db = f'postgresql://{user_db}:{pass_db}@{host_db}:{port_db}/{name_db}'
        return full_url_db