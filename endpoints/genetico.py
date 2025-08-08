from fastapi import APIRouter
from pydantic import BaseModel
from services.genetico import ejecutar_algoritmo_genetico

router = APIRouter()

class NumeroInput(BaseModel):
    sbcNumber: int

@router.post("/generate-team")
def generate_team(input_data: NumeroInput):
    numero = input_data.sbcNumber
    resultado = ejecutar_algoritmo_genetico(numero)
    return {
        "status": "success",
        "message": "Equipo generado exitosamente",
        "data": resultado
    }