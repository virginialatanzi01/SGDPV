from datetime import date
from data.data_estadia import DataEstadia
from entity_models.estadia_model import Estadia

class EstadiaLogic:
    @classmethod
    def crear_reserva(cls, persona_id, tipo_id, f_ingreso, f_egreso, precio_total, cantidad_personas):
        nueva_reserva = Estadia(
            persona_id=persona_id,
            tipo_habitacion_id=tipo_id,
            fecha_ingreso=f_ingreso,
            fecha_egreso=f_egreso,
            precio_total=precio_total,
            estado='Reservada',
            cantidad_personas=cantidad_personas
        )
        DataEstadia.add_estadia(nueva_reserva)
        return nueva_reserva

    @classmethod
    def get_mis_reservas(cls, persona_id):
        todas = DataEstadia.get_estadias_by_persona(persona_id)
        pendientes = []
        historicas = []
        for reserva in todas:
            if reserva.estado in ['Reservada', 'En curso']:
                pendientes.append(reserva)
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
    def modificar_reserva(cls, id, nueva_f_ingreso, nueva_f_egreso, nueva_cantidad_personas):
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
            reserva.cantidad_personas = nueva_cantidad_personas
            DataEstadia.update_estadia()
            return True, "Reserva modificada correctamente"
        else:
            return False, "No hay disponibilidad para las nuevas fechas en este tipo de habitación."

    @classmethod
    def buscar_reservas_por_dni(cls, dni):
        return DataEstadia.get_reservas_pendientes_by_dni(dni)

    @classmethod
    def get_estadias_para_checkout(cls):
        return DataEstadia.get_estadias_checkout_hoy()

    @classmethod
    def realizar_checkout(cls, id):
        reserva = DataEstadia.get_estadia_by_id(id)
        if reserva.estado != 'En curso':
            return False, "La estadía no está en curso."
        # Al dejar de estar 'En curso' o 'Reservada', la habitación se libera automáticamente
        reserva.estado = 'Finalizada'
        DataEstadia.update_estadia()
        return True, "Check-out realizado con éxito."

    @classmethod
    def modificar_fecha_egreso(cls, estadia_id, nueva_fecha_egreso):
        estadia = DataEstadia.get_estadia_by_id(estadia_id)
        if estadia.estado != 'En curso':
            return False, "Solo se pueden modificar estadías en curso."
        if nueva_fecha_egreso <= estadia.fecha_ingreso:
            return False, "La fecha de salida debe ser posterior al ingreso."
        esta_libre = DataEstadia.verificar_disponibilidad_habitacion_fisica(
            estadia.habitacion_id,
            estadia.fecha_ingreso,
            nueva_fecha_egreso,
            estadia.id
        )
        if not esta_libre:
            return False, f"La habitación {estadia.habitacion.nro_habitacion} ya está reservada por otro huésped para esas fechas."
        delta = nueva_fecha_egreso - estadia.fecha_ingreso
        nuevas_noches = delta.days
        nuevo_total = estadia.tipo_habitacion.precio_por_noche * nuevas_noches
        estadia.fecha_egreso = nueva_fecha_egreso
        estadia.precio_total = nuevo_total
        DataEstadia.update_estadia()
        return True, "Fecha de salida modificada correctamente."

    @classmethod
    def procesar_no_shows(cls):
        return DataEstadia.cancelar_reservas_vencidas()

    @classmethod
    def calcular_nuevo_total_early_checkin(cls, estadia_id):
        """Calcula el nuevo precio si se adelanta el ingreso a HOY."""
        reserva = DataEstadia.get_estadia_by_id(estadia_id)
        hoy = date.today()
        if hoy >= reserva.fecha_ingreso:
            return reserva.precio_total
        dias_extra = (reserva.fecha_ingreso - hoy).days
        costo_extra = dias_extra * reserva.tipo_habitacion.precio_por_noche
        return reserva.precio_total + costo_extra