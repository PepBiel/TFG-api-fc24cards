import json
from fastapi import HTTPException

def filter_player_service(player_data):
    try:
        with open("jugadores.json", "r", encoding="utf-8") as f:
            jugadores_data = json.load(f)

        updated_data = []
        found = False

        for player in jugadores_data:
            if "options" in player:
                selected_option = None
                for option in player["options"]:
                    if (option["name"] == player_data.name and
                        option["rating"] == player_data.rating and
                        option["position"] == player_data.position and
                        option["version"] == player_data.version):
                        selected_option = option
                        break
                if selected_option:
                    found = True
                    updated_data.append(selected_option)
                else:
                    updated_data.append(player)
            else:
                updated_data.append(player)

        if not found:
            raise HTTPException(status_code=404, detail="Player not found in options")

        with open("jugadores.json", "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)

        return {"message": "Player filtered successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

def delete_player_service(player_data):
    try:
        with open("jugadores.json", "r", encoding="utf-8") as f:
            jugadores_data = json.load(f)

        updated_data = []
        found = False

        for player in jugadores_data:
            if (player["name"] == player_data.name and
                player["rating"] == player_data.rating and
                player["position"] == player_data.position and
                player["version"] == player_data.version):
                found = True
                continue
            else:
                updated_data.append(player)

        if not found:
            raise HTTPException(status_code=404, detail="Player not found in options")

        with open("jugadores.json", "w", encoding="utf-8") as f:
            json.dump(updated_data, f, ensure_ascii=False, indent=4)

        return {"message": "Player deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")