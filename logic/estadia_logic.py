from datetime import date
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
            estado='Reservada'
        )
        DataEstadia.add_estadia(nueva_reserva)
        return nueva_reserva

    @classmethod
    def get_mis_reservas(cls, persona_id):
        todas = DataEstadia.get_estadias_by_persona(persona_id)
        hoy = date.today()
        pendientes = []
        historicas = []
        for reserva in todas:
            # Pendientes: Estado Reservada/En curso o Fechas futuras/actuales
            if reserva.estado in ['Reservada', 'En curso']:
                pendientes.append(reserva)
            # Históricas: Canceladas, Finalizadas o fechas pasadas
            else:
                historicas.append(reserva)
        return pendientes, historicas

    @classmethod
    def get_one_estadia(cls, id):
        return DataEstadia.get_estadia_by_id(id)

    @classmethod
    def cancelar_reserva(cls, id):
        reserva = DataEstadia.get_estadia_by_id(id)
        if reserva.estado == 'Reservada':
            reserva.estado = 'Cancelada'
            DataEstadia.update_estadia()
            return True
        return False

    @classmethod
    def modificar_reserva(cls, id, nueva_f_ingreso, nueva_f_egreso):
        reserva = DataEstadia.get_estadia_by_id(id)
        disponibles = DataEstadia.get_disponibilidad(
            reserva.tipo_habitacion_id,
            nueva_f_ingreso,
            nueva_f_egreso,
            ignorar_reserva_id=id
        )
        if disponibles > 0:
            delta = nueva_f_egreso - nueva_f_ingreso
            noches = delta.days
            precio_noche = reserva.tipo_habitacion.precio_por_noche
            nuevo_total = precio_noche * noches
            reserva.fecha_ingreso = nueva_f_ingreso
            reserva.fecha_egreso = nueva_f_egreso
            reserva.precio_total = nuevo_total
            DataEstadia.update_estadia()
            return True, "Reserva modificada correctamente"
        else:
            return False, "No hay disponibilidad para las nuevas fechas en este tipo de habitación."