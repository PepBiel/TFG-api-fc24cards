import easyocr
import os
import json
import base64
from OCR_YOLO import (
    get_images,
    verify_image_counts,
    process_image_data,
    search_player_database,
    Jugador,
    normalize_price,
    normalize_positions
)

def ejecutar_ocr():
    general_path = 'segmentations_YOLO'

    folders = {
        "name": f"{general_path}/name",
        "overall": f"{general_path}/overall",
        "position": f"{general_path}/position",
        "pace": f"{general_path}/pace",
        "shooting": f"{general_path}/shooting",
        "passing": f"{general_path}/passing",
        "dribbling": f"{general_path}/dribbling",
        "defending": f"{general_path}/defending",
        "physicallity": f"{general_path}/phisicallity",
        "cards": f"{general_path}/cards"
    }

    # Verificar que todas las carpetas tienen el mismo número de imágenes
    verify_image_counts(list(folders.values()))

    reader = easyocr.Reader(['es'])
    players = []
    images = {k: get_images(v) for k, v in folders.items()}

    total = len(images["name"])  # Todas deberían tener el mismo número si están sincronizadas

    for i in range(total):
        try:
            result = process_image_data(
                reader,
                images["name"][i], images["overall"][i], images["position"][i],
                images["pace"][i], images["shooting"][i], images["passing"][i],
                images["dribbling"][i], images["defending"][i], images["physicallity"][i]
            )

            player = search_player_database(
                result["name"], result["overall"], result["position"],
                result["pace"], result["shooting"], result["passing"],
                result["dribbling"], result["defending"], result["physicallity"]
            )

            if isinstance(player, list) and len(player) > 1:
                players.append({
                    "options": [
                        {
                            "name": p["name"],
                            "rating": p["rating"],
                            "position": normalize_positions(p["position"]),
                            "price": normalize_price(p["price"]),
                            "club": p["club"],
                            "nacionality": p["nationality"],
                            "league": p["league"],
                            "version": p["version"],
                            "pace": p["pace"],
                            "shooting": p["shooting"],
                            "passing": p["passing"],
                            "dribbling": p["dribbling"],
                            "defending": p["defending"],
                            "phisicality": p["physicality"],
                            "foot": p["foot"],
                            "weakFoot": p["weak_foot"],
                            "skills": p["skills"],
                            "body": p["body"],
                            "gender": p["gender"],
                            "image": os.path.basename(images["cards"][i])
                        }
                        for p in player
                    ]
                })
            elif isinstance(player, list) and len(player) == 1:
                player = player[0]
                players.append({
                    "name": player["name"],
                    "rating": player["rating"],
                    "position": normalize_positions(player["position"]),
                    "price": normalize_price(player["price"]),
                    "club": player["club"],
                    "nacionality": player["nationality"],
                    "league": player["league"],
                    "version": player["version"],
                    "pace": player["pace"],
                    "shooting": player["shooting"],
                    "passing": player["passing"],
                    "dribbling": player["dribbling"],
                    "defending": player["defending"],
                    "phisicality": player["physicality"],
                    "foot": player["foot"],
                    "weakFoot": player["weak_foot"],
                    "skills": player["skills"],
                    "body": player["body"],
                    "gender": player["gender"],
                    "image": os.path.basename(images["cards"][i])
                })

        except Exception as e:
            print(f"⚠️ Error procesando OCR para imagen {i}: {e}")
            continue  # Saltar al siguiente si algo falla

    # Guardar resultados
    with open("jugadores.json", 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=4)

    # Leer el JSON generado
    with open("jugadores.json", 'r', encoding='utf-8') as f:
        jugadores_data = json.load(f)

    # Convertir imágenes a Base64 solo para la respuesta
    for player in jugadores_data:
        if "image" in player:
            image_path = os.path.join(folders["cards"], player["image"])
            try:
                with open(image_path, "rb") as img_file:
                    player["image"] = base64.b64encode(img_file.read()).decode("utf-8")
            except Exception as e:
                print(f"⚠️ Error encoding image {image_path}: {e}")
                player["image"] = None  # Set to None if encoding fails
        elif "options" in player:
            for option in player["options"]:
                if "image" in option:
                    image_path = os.path.join(folders["cards"], option["image"])
                    try:
                        with open(image_path, "rb") as img_file:
                            option["image"] = base64.b64encode(img_file.read()).decode("utf-8")
                    except Exception as e:
                        print(f"⚠️ Error encoding image {image_path}: {e}")
                        option["image"] = None
        else:
            print(f"⚠️ Player data does not contain an 'image' key: {player}")

    return {
        "status": "success",
        "jugadores_guardados": len(players),
        "data": jugadores_data
    }

