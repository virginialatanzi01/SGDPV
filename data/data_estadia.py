from data.database import Database
from entity_models.estadia_model import Estadia
from entity_models.habitacion_model import Habitacion
from entity_models.persona_model import Persona
from sqlalchemy import and_
from flask import current_app as app

class DataEstadia:
    @classmethod
    def add_estadia(cls, estadia):
        try:
            Database.db.session.add(estadia)
            Database.db.session.commit()
        except Exception as e:
            Database.db.session.rollback()
            raise e

    @classmethod
    def get_estadia_by_id(cls, id):
        return Estadia.query.get_or_404(id)

    @classmethod
    def get_estadias_by_persona(cls, persona_id):
        try:
            return Estadia.query.filter_by(persona_id=persona_id).order_by(Estadia.fecha_ingreso.desc()).all()
        except Exception as e:
            app.logger.error(f"Error al obtener estadías: {e}")
            return []

    @classmethod
    def update_estadia(cls):
        try:
            Database.db.session.commit()
        except Exception as e:
            Database.db.session.rollback()
            raise e

    @classmethod
    def get_disponibilidad(cls, tipo_id, f_ingreso, f_egreso, ignorar_reserva_id=None):
        total_habitaciones = Habitacion.query.filter_by(tipo_id=tipo_id).count()
        query = Estadia.query.filter(
            Estadia.tipo_habitacion_id == tipo_id,
            Estadia.estado.in_(['Reservada', 'En curso']),
            and_(Estadia.fecha_ingreso < f_egreso, Estadia.fecha_egreso > f_ingreso)
        )
        if ignorar_reserva_id:
            query = query.filter(Estadia.id != ignorar_reserva_id)
        reservas_ocupadas = query.count()
        return total_habitaciones - reservas_ocupadas

    @classmethod
    def get_reservas_pendientes(cls):
        return Estadia.query.filter_by(estado='Reservada').order_by(Estadia.fecha_ingreso).all()

    @classmethod
    def get_reservas_pendientes_by_dni(cls, dni):
        try:
            return Estadia.query.join(Persona).filter(
                Persona.nro_documento == dni,
                Estadia.estado == 'Reservada'
            ).order_by(Estadia.fecha_ingreso).all()
        except Exception as e:
            app.logger.error(f"Error al buscar reservas por DNI: {e}")
            return []

    @classmethod
    def get_habitaciones_ocupadas_ids(cls, f_ingreso, f_egreso):
        ocupadas = Estadia.query.with_entities(Estadia.habitacion_id).filter(
            Estadia.habitacion_id.isnot(None),
            Estadia.estado.in_(['Reservada', 'En curso']),
            and_(Estadia.fecha_ingreso < f_egreso, Estadia.fecha_egreso > f_ingreso)
        ).all()
        return [r[0] for r in ocupadas]