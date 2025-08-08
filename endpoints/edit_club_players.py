from fastapi import APIRouter
from pydantic import BaseModel
from services.edit_club_players_service import filter_player_service, delete_player_service

router = APIRouter()

class PlayerData(BaseModel):
    name: str
    rating: int
    position: str
    version: str

@router.post("/filter-player")
def filter_player(player_data: PlayerData):
    return filter_player_service(player_data)

@router.post("/delete-player")
def delete_player(player_data: PlayerData):
    return delete_player_service(player_data)