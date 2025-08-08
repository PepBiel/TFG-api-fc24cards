# endpoints/segmentation.py

from fastapi import APIRouter
from services.segmentation_YOLO import procesar_segmentacion

router = APIRouter()

@router.post("/process-segmentation")
def segment_images():
    message = procesar_segmentacion()
    return {"status": "success", "message": message}
