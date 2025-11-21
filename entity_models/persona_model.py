from werkzeug.security import generate_password_hash, check_password_hash
from data.database import Database

db = Database.db

# Tipos de personas admitidos: {cliente, administrador}

class Persona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo_documento = db.Column(db.String(20))
    nro_documento = db.Column(db.String(8))
    nombre = db.Column(db.String(150))
    apellido = db.Column(db.String(150))
    fecha_nacimiento = db.Column(db.Date)
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(25))
    nombre_usuario = db.Column(db.String(80), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    tipo_persona = db.Column(db.String(40))

    def to_dict(self):
        return {
            'id': self.id,
            'tipo_documento': self.tipo_documento,
            'nro_documento': self.nro_documento,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'fecha_nacimiento': self.fecha_nacimiento,
            'email': self.email,
            'telefono': self.telefono,
            'nombre_usuario': self.nombre_usuario,
            'contrasena': self.contrasena,
            'tipo_persona': self.tipo_persona,
        }

    # Deserialización: convierte el objeto JSON en un objeto Persona
    @classmethod
    def from_dict(cls, data):
        persona = cls()
        persona.id = data['id']
        persona.tipo_documento = data['tipo_documento']
        persona.nro_documento = data['nro_documento']
        persona.nombre = data['nombre']
        persona.apellido = data['apellido']
        persona.fecha_nacimiento = data['fecha_nacimiento']
        persona.email = data['email']
        persona.telefono = data['telefono']
        persona.nombre_usuario = data['nombre_usuario']
        persona.contrasena = data['contrasena']
        persona.tipo_persona = data['tipo_persona']
        return persona

    def establece_contrasena(self, contrasena):
        self.contrasena = generate_password_hash(contrasena)

    def valida_contrasena(self, contrasena):
        return check_password_hash(self.contrasena, contrasena)