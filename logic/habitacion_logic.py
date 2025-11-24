from data.data_habitacion import DataHabitacion
from data.data_estadia import DataEstadia  # <--- IMPORTACIÓN NECESARIA

class HabitacionLogic:
    @classmethod
    def get_all_habitaciones(cls):
        habitaciones = DataHabitacion.get_all_habitaciones()
        return habitaciones

    @classmethod
    def get_one_habitacion(cls, nro_habitacion):
        habitacion = DataHabitacion.get_one_habitacion(nro_habitacion)
        return habitacion

    @classmethod
    def add_habitacion(cls, habitacion):
        DataHabitacion.add_habitacion(habitacion)

    @classmethod
    def update_existencia(cls):
        DataHabitacion.update_existencia()

    @classmethod
    def delete_habitacion(cls, nro_habitacion):
        DataHabitacion.delete_habitacion(nro_habitacion)

    @classmethod
    def get_habitacion_disponible_by_tipo(cls, tipo_id, f_ingreso, f_egreso):
        habitaciones_del_tipo = DataHabitacion.get_habitaciones_by_tipo(tipo_id)
        habitaciones_ocupadas_ids = DataEstadia.get_habitaciones_ocupadas_ids(f_ingreso, f_egreso)
        for habitacion in habitaciones_del_tipo:
            if habitacion.id not in habitaciones_ocupadas_ids:
                return habitacion
        return None