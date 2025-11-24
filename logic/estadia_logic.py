from data.data_estadia import DataEstadia
from entity_models.estadia_model import Estadia

class EstadiaLogic:
    @classmethod
    def crear_reserva(cls, persona_id, tipo_id, f_ingreso, f_egreso, precio_total):
        nueva_reserva = Estadia(
            persona_id=persona_id,
            tipo_habitacion_id=tipo_id,
            fecha_ingreso=f_ingreso,
            fecha_egreso=f_egreso,
            precio_total=precio_total,
            estado='Reservada' # RN 6
        )
        DataEstadia.add_estadia(nueva_reserva)
        return nueva_reserva