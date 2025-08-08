from fastapi import APIRouter
from services.ocr import ejecutar_ocr

router = APIRouter()

@router.post("/process-ocr")
def ocr_images():
    return ejecutar_ocr()
