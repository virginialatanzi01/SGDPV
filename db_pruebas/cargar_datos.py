from flask import Flask
from data.database import Database
from entity_models.habitacion_model import Habitacion
from entity_models.tipo_habitacion_model import TipoHabitacion

# Configura la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Database.configura_conexion()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Database.db.init_app(app)

# Carga de habitaciones
with app.app_context():
    tipos_habitacion = TipoHabitacion.query.all()

    habitaciones = []
    base_numero = 100  # Primer bloque de habitaciones

    for tipo in tipos_habitacion:
        for i in range(10):  # Crear 10 habitaciones por tipo
            nueva_habitacion = Habitacion(
                nro_habitacion=str(base_numero + i),  # Convertir a string si es necesario
                tipo_id=tipo.id
            )
            habitaciones.append(nueva_habitacion)

        base_numero += 100  # Saltar al siguiente bloque (200, 300, etc.)

    Database.db.session.add_all(habitaciones)
    Database.db.session.commit()

    print("Habitaciones cargadas correctamente.")
