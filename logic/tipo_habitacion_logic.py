from data.data_tipo_habitacion import DataTipoHabitacion
from data.data_estadia import DataEstadia
from data.database import Database
from entity_models.tipo_habitacion_model import TipoHabitacion

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
        Database.db.session.add(nuevo_tipo)
        Database.db.session.commit()
        return nuevo_tipo

    @classmethod
    def buscar_tipos_disponibles(cls, fecha_desde, fecha_hasta, cantidad_personas):
        # En el futuro, cruzo con  tabla 'estadia' para ver disponibilidad real por fechas.
        # Por ahora, filtramos solo por capacidad según el requerimiento actual.
        return DataTipoHabitacion.get_tipos_by_capacidad(cantidad_personas)

    @classmethod
    def buscar_tipos_disponibles(cls, fecha_desde, fecha_hasta, cantidad_personas):
        tipos_capacidad = DataTipoHabitacion.get_tipos_by_capacidad(cantidad_personas)
        tipos_disponibles = []
        for tipo in tipos_capacidad:
            disponibles = DataEstadia.get_disponibilidad(tipo.id, fecha_desde, fecha_hasta)
            if disponibles > 0:
                tipos_disponibles.append(tipo)
        return tipos_disponibles