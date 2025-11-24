from entity_models.servicio_model import Servicio
from entity_models.consumo_model import Consumo
from data.database import Database
from flask import current_app as app

class DataServicio:
    @classmethod
    def get_all(cls):
        return Servicio.query.all()

    @classmethod
    def get_by_id(cls, id):
        return Servicio.query.get_or_404(id)

    @classmethod
    def add_consumo(cls, consumo):
        try:
            Database.db.session.add(consumo)
            Database.db.session.commit()
        except Exception as e:
            Database.db.session.rollback()
            raise e