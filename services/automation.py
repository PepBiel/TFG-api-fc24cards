from PIL import ImageGrab
from datetime import datetime
import os
import time
import threading
import winsound
import shutil
import base64

CAPTURA_CARPETA = "images/"
TEMP_CARPETA = "temp_captures/"

# Crear carpetas si no existen
for folder in [CAPTURA_CARPETA, TEMP_CARPETA]:
    if not os.path.exists(folder):
        os.makedirs(folder)

_capture_thread = None
_stop_event = threading.Event()
_interval_segons = 5  # Valor por defecto
_captures = []  # Lista para almacenar las capturas realizadas

def fer_captura():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(TEMP_CARPETA, f"{timestamp}.png")
    captura = ImageGrab.grab()
    captura.save(filepath, "PNG")
    print(f"📸 Captura guardada temporalmente: {filepath}")
    # Emitir un sonido
    winsound.Beep(1000, 500)  # Frecuencia: 1000 Hz, Duración: 500 ms
    _captures.append(filepath)  # Agregar la captura a la lista
    return filepath

def captura_unica():
    return fer_captura()

def _bucle_captura():
    global _interval_segons
    while not _stop_event.is_set():
        fer_captura()
        time.sleep(_interval_segons)

def iniciar_bucle(intervalo):
    global _capture_thread, _interval_segons, _captures
    _interval_segons = max(1, intervalo)  # mínimo 1 segundo
    _captures = []  # Reiniciar la lista de capturas
    if _capture_thread is None or not _capture_thread.is_alive():
        _stop_event.clear()
        _capture_thread = threading.Thread(target=_bucle_captura, daemon=True)
        _capture_thread.start()
        return True
    return False

def detener_bucle():
    _stop_event.set()
    return _captures  # Devolver la lista de capturas realizadas

def guardar_capturas(capturas):
    guardadas = []
    for capture in capturas:
        if capture.file and os.path.exists(capture.file):
            # Guardar archivo desde una ruta
            destino = os.path.join(CAPTURA_CARPETA, os.path.basename(capture.file))
            shutil.move(capture.file, destino)
            guardadas.append(destino)
        elif capture.image_base64:
            # Guardar archivo desde Base64
            try:
                image_data = base64.b64decode(capture.image_base64)
                filename = f"manual_{len(guardadas)}.png"
                filepath = os.path.join(CAPTURA_CARPETA, filename)
                with open(filepath, "wb") as f:
                    f.write(image_data)
                guardadas.append(filepath)
            except Exception as e:
                print(f"Error al guardar imagen Base64: {e}")
    eliminar_capturas_temporales()
    return guardadas

def eliminar_capturas_temporales():
    if os.path.exists(TEMP_CARPETA):
        # Eliminar todos los archivos y la carpeta
        shutil.rmtree(TEMP_CARPETA)
        # Recrear la carpeta vacía
        os.makedirs(TEMP_CARPETA)