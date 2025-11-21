from data.data_tipo_habitacion import DataTipoHabitacion

class TipoHabitacionLogic:
    @classmethod
    def get_all_tipos(cls):
        tipos = DataTipoHabitacion.get_all_tipos()
        return tipos

    @classmethod
    def get_one_tipo(cls, id):
        tipo = DataTipoHabitacion.get_one_tipo(id)
        return tipo

    @classmethod
    def get_tipo_by_desc(cls, descripcion):
        tipo = DataTipoHabitacion.get_tipo_by_desc(descripcion)
        return tipo

    @classmethod
    def add_tipo(cls, tipo):
        DataTipoHabitacion.add_tipo(tipo)

    @classmethod
    def delete_tipo(cls, id):
        DataTipoHabitacion.delete_tipo(id)