# services/genetico.py

import os
import json
import base64
from algritmo_genetico import genetic_algorithm
import copy

def ejecutar_algoritmo_genetico(numero):
    # Cargar requisitos del archivo sbc.json
    with open("sbc.json", "r", encoding='utf-8') as file:
        requirements_data = json.load(file)

    # Seleccionar el primer conjunto de requisitos
    target_team = requirements_data['teams'][numero]

    # Ejecutar el algoritmo
    best_team = genetic_algorithm(target_team)

    # Crear una copia del equipo para evitar modificar el original
    team_copy = copy.deepcopy(best_team)

    # Convertir imágenes a Base64 solo para la respuesta
    for player in team_copy[0]:
        image_name = player["player"].get("image")  # Usar .get() para evitar KeyError
        print(f"Nombre de la imagen {image_name}")
        if image_name:  # Validar que no sea None
            image_path = os.path.join("segmentations_YOLO/cards", image_name)
            try:
                with open(image_path, "rb") as img_file:
                    player["player"]["image"] = base64.b64encode(img_file.read()).decode("utf-8")
            except Exception as e:
                print(f"⚠️ Error encoding image {image_path}: {e}")
                player["player"]["image"] = None  # Set to None if encoding fails
        else:
            player["player"]["image"] = None  # Si no hay imagen, establecer como None

    # Formato JSON serializable
    team_data = {
        "team": team_copy[0],        # Lista de jugadores
        "team_info": team_copy[1],   # Info del equipo
        "fitness": team_copy[2]      # Valor de fitness
    }

    # Guardar en archivo
    with open("best_team.json", "w", encoding="utf-8") as file:
        json.dump(team_data, file, ensure_ascii=False, indent=4)

    return team_data
