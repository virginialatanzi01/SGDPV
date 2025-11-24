from data.data_servicio import DataServicio
from entity_models.consumo_model import Consumo

class ServicioLogic:
    @classmethod
    def get_all_servicios(cls):
        return DataServicio.get_all()

    @classmethod
    def registrar_consumo(cls, estadia_id, servicio_id, cantidad):
        servicio = DataServicio.get_by_id(servicio_id)

        nuevo_consumo = Consumo(
            estadia_id=estadia_id,
            servicio_id=servicio_id,
            cantidad=cantidad,
            precio_unitario_historico=servicio.precio
        )
        DataServicio.add_consumo(nuevo_consumo)
        return nuevo_consumo