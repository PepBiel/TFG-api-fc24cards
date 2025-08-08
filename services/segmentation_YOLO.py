# services/segmentation.py

import os
import cv2
from ultralytics import YOLO

def procesar_segmentacion(
    carpeta_imagenes='images',
    ruta_modelo_cartas='models/cardsDetection-v2.pt',
    ruta_modelo_etiquetas='models/elementsDetection.pt',
    output_folder='segmentations_YOLO'
):
    umbral_confianza_cartas = 0.1
    umbral_confianza_etiquetas = 0.1
    labels = ['Overall', 'Name', 'Defending', 'Dribbling', 'Pace', 'Shooting', 'Phisicallity', 'Position', 'Passing']

    output_folder_cartas = os.path.join(output_folder, 'cards')
    cards_detections_folder = os.path.join(output_folder, 'cardsDetections')
    elements_detections_folder = os.path.join(output_folder, 'elementsDetections')

    os.makedirs(output_folder_cartas, exist_ok=True)
    os.makedirs(cards_detections_folder, exist_ok=True)
    os.makedirs(elements_detections_folder, exist_ok=True)
    label_dirs = {label: os.path.join(output_folder, label.lower()) for label in labels}
    for dir in label_dirs.values():
        os.makedirs(dir, exist_ok=True)

    model_cartas = YOLO(ruta_modelo_cartas)
    model_etiquetas = YOLO(ruta_modelo_etiquetas)

    global_idx = 0

    for nombre_imagen in sorted(os.listdir(carpeta_imagenes)):
        ruta_imagen = os.path.join(carpeta_imagenes, nombre_imagen)
        if not ruta_imagen.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue

        print(f"📸 Procesando imagen: {nombre_imagen}")
        results_cartas = model_cartas(ruta_imagen)[0]
        image = cv2.imread(ruta_imagen)

        for box, score, cls in zip(results_cartas.boxes.xyxy, results_cartas.boxes.conf, results_cartas.boxes.cls):
            if score < umbral_confianza_cartas:
                continue

            x1, y1, x2, y2 = map(int, box.tolist())
            crop = image[y1:y2, x1:x2]

            crop_path = os.path.join(output_folder_cartas, f'card_{global_idx}.png')
            cv2.imwrite(crop_path, crop)

            results_etiquetas = model_etiquetas(crop_path)[0]
            crop_with_boxes = crop.copy()
            saved = False

            for box, score, cls in zip(results_etiquetas.boxes.xyxy, results_etiquetas.boxes.conf, results_etiquetas.boxes.cls):
                label = model_etiquetas.names[int(cls)]
                if score < umbral_confianza_etiquetas or label not in labels:
                    continue

                x1, y1, x2, y2 = map(int, box.tolist())
                label_crop = crop[y1:y2, x1:x2]
                label_path = os.path.join(label_dirs[label], f'{label.lower()}_{global_idx}.png')
                cv2.imwrite(label_path, label_crop)
                saved = True

            if saved:
                cv2.imwrite(os.path.join(elements_detections_folder, f'card_with_boxes_{global_idx}.png'), crop_with_boxes)

            global_idx += 1

        cv2.imwrite(os.path.join(cards_detections_folder, f'image_with_boxes_{nombre_imagen}'), image)

    return f"Segmentación completada. {global_idx} cartas procesadas."
