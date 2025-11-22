from data.data_tipo_habitacion import DataTipoHabitacion
from entity_models.tipo_habitacion_model import TipoHabitacion
from data.database import Database

class TipoHabitacionLogic:
    @classmethod
    def get_all_tipos(cls):
        return DataTipoHabitacion.get_all_tipos()

    @classmethod
    def get_one_tipo(cls, id):
        return DataTipoHabitacion.get_one_tipo(id)

    @classmethod
    def add_tipo_habitacion(cls, denominacion, descripcion, capacidad_personas, precio_por_noche, nombre_imagen):
        # Creamos la instancia del objeto
        nuevo_tipo = TipoHabitacion(
            denominacion=denominacion,
            descripcion=descripcion,
            capacidad_personas=capacidad_personas,
            precio_por_noche=precio_por_noche,
            nombre_imagen=nombre_imagen
        )
        # Lo guardamos usando la capa de datos o directamente aquí si es simple
        Database.db.session.add(nuevo_tipo)
        Database.db.session.commit()
        return nuevo_tipo