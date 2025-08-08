from fastapi import APIRouter
from pydantic import BaseModel
import base64
from typing import Optional
from services.automation import captura_unica, iniciar_bucle, detener_bucle, guardar_capturas

router = APIRouter()

class IntervalRequest(BaseModel):
    interval: int  # en segundos

class CaptureItem(BaseModel):
    file: Optional[str] = None
    image_base64: Optional[str] = None

class SaveCapturesRequest(BaseModel):
    captures: list[CaptureItem]
@router.post("/capture")
def capture_once():
    filepath = captura_unica()
    return {"status": "success", "message": "Captura realizada", "file": filepath}

@router.post("/start-capture-loop")
def start_capture_loop(request: IntervalRequest):
    started = iniciar_bucle(request.interval)
    if started:
        return {
            "status": "success",
            "message": f"Bucle de captura iniciado cada {request.interval} segundos"
        }
    else:
        return {"status": "already_running", "message": "El bucle ya estaba en ejecución"}

# ---------- ACCIÓN (POST) ----------
@router.post("/stop-capture-loop")
def stop_capture_loop():
    captures = detener_bucle()              # <- tu función que para el hilo y devuelve la lista de ficheros
    base64_captures = []
    for filepath in captures:
        with open(filepath, "rb") as img:
            base64_captures.append(
                {
                    "file": filepath,
                    "image_base64": base64.b64encode(img.read()).decode(),
                }
            )
    return {
        "status": "success",
        "message": "Bucle de captura detenido",
        "captures": base64_captures,
    }

@router.post("/save-captures")
def save_captures(request: SaveCapturesRequest):
    saved_files = guardar_capturas(request.captures)
    return {
        "status": "success",
        "message": f"{len(saved_files)} capturas guardadas",
        "files": saved_files,
    }
