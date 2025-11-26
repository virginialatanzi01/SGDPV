from app import app
from data.database import Database
from entity_models.persona_model import Persona
from datetime import date

with app.app_context():
    if not Persona.query.filter_by(nombre_usuario='admin').first():
        admin = Persona()
        admin.nombre = "Admin"
        admin.apellido = "Sistema"
        admin.tipo_documento = "DNI"
        admin.nro_documento = "12345678"
        admin.fecha_nacimiento = date(1990, 1, 1)
        admin.email = "admin@hotel.com"
        admin.telefono = "111222333"
        admin.nombre_usuario = "admin"  # <--- TU USUARIO
        admin.tipo_persona = "administrador"

        admin.establece_contrasena("admin")

        Database.db.session.add(admin)
        Database.db.session.commit()
    else:
        print("El usuario 'admin' ya existe.")