from data.data_habitacion import DataHabitacion

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