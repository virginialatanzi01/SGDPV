from app import app
from data.database import Database
from entity_models.tipo_habitacion_model import TipoHabitacion
from entity_models.habitacion_model import Habitacion


def cargar_datos():
    with app.app_context():
        print("Iniciando carga de alojamientos...")

        # 1. Crear Tipos de Habitación
        # Asegúrate de que los nombres de las imágenes coincidan con lo que tienes en static/imagenes_tipos_habitaciones/
        tipos = [
            {
                "denominacion": "Habitación Doble Twin",
                "descripcion": "Habitación con dos camas individuales, perfecta para amigos, compañeros de trabajo o huéspedes que prefieren camas separadas. Cuenta con baño privado, escritorio y Wi-Fi.",
                "capacidad": 2,
                "precio": 50000.0,
                "imagen": "doble_twin.jpg",
                "habitaciones": ["101", "102", "103"]
            },
            {
                "denominacion": "Habitación Doble Matrimonial",
                "descripcion": "Habitación cómoda con una cama matrimonial ideal para parejas o viajeros que buscan más espacio y confort. Incluye baño privado, climatización y servicio de Wi-Fi.",
                "capacidad": 2,
                "precio": 60000.0,
                "imagen": "doble_matrimonial.jpg",
                "habitaciones": ["104", "105", "106", "107"]
            },
            {
                "denominacion": "Habitación Triple Mixta",
                "descripcion": "Habitación equipada con una cama grande y una cama individual, cómoda para familias pequeñas, parejas con un hijo o grupos con diferentes necesidades de descanso.",
                "capacidad": 3,
                "precio": 80000.0,
                "imagen": "triple_mixta.jpg",
                "habitaciones": ["108", "109"]
            },
            {
                "denominacion": "Habitación Individual",
                "descripcion": "Habitación práctica y confortable para un huésped, con una cama individual, baño privado, climatización y acceso a Wi-Fi.",
                "capacidad": 1,
                "precio": 35000.0,
                "imagen": "individual.jpg",
                "habitaciones": ["110"]
            },
            {
                "denominacion": "Habitación Familiar",
                "descripcion": "Espaciosa habitación equipada con dos camas grandes, ideal para familias o grupos pequeños que desean compartir un espacio amplio y cómodo. Incluye baño privado, frigobar y Wi-Fi.",
                "capacidad": 4,
                "precio": 90000.0,
                "imagen": "familiar.jpg",
                "habitaciones": ["111", "112", "113"]
            },
            {
                "denominacion": "Habitación Tiple Individual",
                "descripcion": "Habitación con tres camas individuales, ideal para grupos de amigos, equipos de trabajo o viajeros que desean camas separadas. Incluye baño privado y Wi-Fi.",
                "capacidad": 3,
                "precio": 75000.0,
                "imagen": "triple_individual.jpg",
                "habitaciones": ["114", "115"]
            }
        ]

        for data in tipos:
            # Verificar si existe el tipo para no duplicar
            tipo_existente = TipoHabitacion.query.filter_by(denominacion=data["denominacion"]).first()

            if not tipo_existente:
                nuevo_tipo = TipoHabitacion(
                    denominacion=data["denominacion"],
                    descripcion=data["descripcion"],
                    capacidad_personas=data["capacidad"],
                    precio_por_noche=data["precio"],
                    nombre_imagen=data["imagen"]
                )
                Database.db.session.add(nuevo_tipo)
                Database.db.session.commit()  # Commit para obtener el ID
                print(f"Tipo creado: {nuevo_tipo.denominacion}")

                tipo_id = nuevo_tipo.id
            else:
                print(f"Tipo existente: {tipo_existente.denominacion}")
                tipo_id = tipo_existente.id

            # Cargar habitaciones físicas para este tipo
            for nro in data["habitaciones"]:
                hab_existente = Habitacion.query.filter_by(nro_habitacion=nro).first()
                if not hab_existente:
                    nueva_hab = Habitacion(nro_habitacion=nro, tipo_id=tipo_id)
                    Database.db.session.add(nueva_hab)
                    print(f"  - Habitación {nro} creada.")
                else:
                    print(f"  - Habitación {nro} ya existe.")

        Database.db.session.commit()


if __name__ == '__main__':
    cargar_datos()