from flask import Flask
from data.database import Database
from entity_models.tipo_habitacion_model import TipoHabitacion

# Configura la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Database.configura_conexion()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Database.db.init_app(app)

# Consulta los datos
with app.app_context():
    tipos_habitacion = TipoHabitacion.query.all()
    for tipo in tipos_habitacion:
        print(f"""
        ID: {tipo.id}
        Denominación: {tipo.denominacion}
        Descripción: {tipo.descripcion}
        Foto: {tipo.foto}
        Capacidad de personas: {tipo.capacidad_personas}
        Precio por día: {tipo.precio_por_dia}
        """)
