# Backend – Generador automático de DCP (TFG)

## 📌 Descripción general

Este repositorio contiene el backend del Trabajo de Fin de Grado “Tècniques evolutives per a la presa de decisions en videojocs”, cuyo objetivo es automatizar la generación de plantillas óptimas para Desafíos de Creación de Plantillas (DCP) del modo Ultimate Team de EA Sports FC 24.

El backend implementa toda la lógica de negocio del sistema:

- Captura automática de imágenes del videojuego
- Segmentación de cartas mediante visión por computador
- Extracción de información textual mediante OCR
- Identificación y enriquecimiento de jugadores usando base de datos
- Generación de plantillas óptimas mediante algoritmos genéticos
- Exposición de la funcionalidad mediante una API REST

Este backend está diseñado para ser consumido por una interfaz gráfica (frontend), manteniendo una separación clara entre presentación y lógica de cálculo.

## 🏗️ Arquitectura del sistema

El backend sigue una arquitectura modular por capas, donde cada módulo es responsable de una parte concreta del flujo de procesamiento:

```scss
Captura de pantalla
        ↓
Segmentación (YOLO)
        ↓
OCR
        ↓
Enriquecimiento (Base de datos)
        ↓
Algoritmo genético
```

## 🧩 Estructura del proyecto

```bash
backend/
│
├── main.py                     # Punto de entrada de la API
│
├── endpoints/                  # Endpoints REST
│   ├── capture.py              # Captura automática de pantalla
│   ├── segmentation.py         # Segmentación de cartas (YOLO)
│   ├── ocr.py                  # OCR de cartas
│   ├── genetico.py             # Generación de plantillas (AG)
│   └── edit_club_players.py    # Filtrado y borrado de jugadores
│
├── services/                   # Lógica de negocio
│   ├── automation.py           # Capturas automáticas
│   ├── segmentation_YOLO.py    # Modelo YOLO
│   ├── ocr.py                  # Procesamiento OCR
│   ├── genetico.py             # Algoritmo genético
│   └── edit_club_players_service.py
│
├── models/                     # Diferentes modelos para la segmentación
│
├── algoritmo_genetico.py       # Base de este proyecto que nos permite crear las plantillas
│
├── OCR_YOLO.py                 # Contiene todas las funciones que se van a usar en services/ocr.py
│
└── sbc.json                    # Distintas creaciones de plantillas, es decir, los distintos requisitos que requieren los distintos retos
```

## 🚀 Tecnologías utilizadas

- **Python 3**
- **FastAPI** – Framework para la API REST
- **OpenCV** – Procesamiento de imágenes
- **YOLOv8** (Ultralytics) – Detección de cartas
- **easyOCR** – Reconocimiento óptico de caracteres
- **Pillow** (PIL) – Captura de pantalla
- **MySQL** – Base de datos de jugadores

## 🚀 Tecnologías utilizadas

- **Python 3**
- **FastAPI** – API REST
- **OpenCV** – Procesamiento de imágenes
- **YOLOv8 (Ultralytics)** – Detección de cartas
- **easyOCR** – Reconocimiento óptico de caracteres
- **Pillow (PIL)** – Captura de pantalla
- **MySQL** – Base de datos de jugadores
- **Algoritmos genéticos** – Optimización de plantillas

## ⚙️ Instalación y ejecución

### 1️⃣ Crear entorno virtual (recomendado)

```bash
conda create -n tfg-backend python=3.10
conda activate tfg-backend
```

### 2️⃣ Instalar dependencias

```bash
pip install fastapi uvicorn pydantic opencv-python pillow ultralytics easyocr pymysql
```

### 3️⃣ Ejecutar el backend

```bash
uvicorn main:app --reload
```

### La API estará disponible en:

```bash
http://localhost:8000
```

### Documentación automática (Swagger):

```bash
http://localhost:8000/docs
```

## 🔌 Endpoints principales

### 📷 Captura de pantalla

| Método | Endpoint                  | Descripción                |
| ------ | ------------------------- | -------------------------- |
| POST   | `/api/capture`            | Realiza una captura única  |
| POST   | `/api/start-capture-loop` | Inicia captura automática  |
| POST   | `/api/stop-capture-loop`  | Detiene captura automática |
| POST   | `/api/save-captures`      | Guarda capturas recibidas  |

<img width="2560" height="1440" alt="image" src="https://github.com/user-attachments/assets/e23e7c61-a3b5-4bae-9137-d2f4575bc0d6" />

<img width="1600" height="900" alt="image" src="https://github.com/user-attachments/assets/cebed0dc-14ef-4900-931f-2f36e7e763d2" />

### 🧠 Procesamiento de imágenes

| Método | Endpoint                    | Descripción                  |
| ------ | --------------------------- | ---------------------------- |
| POST   | `/api/process-segmentation` | Detecta y segmenta cartas    |
| POST   | `/api/process-ocr`          | Ejecuta OCR sobre las cartas |

<img width="2560" height="1440" alt="image" src="https://github.com/user-attachments/assets/53155d18-db00-4026-9159-c759d6c4ee97" />

<img width="329" height="450" alt="image" src="https://github.com/user-attachments/assets/d6deefd0-266c-4c9e-b2a8-2196a4f07582" />

<img width="1600" height="900" alt="image" src="https://github.com/user-attachments/assets/7963de40-d36f-4ab2-917b-d9b9258551a5" />

<img width="420" height="586" alt="image" src="https://github.com/user-attachments/assets/f0d3d721-a1d8-4e8f-8a0b-c292c4fe5d80" />


### ⚽ Gestión de jugadores

| Método | Endpoint             | Descripción                 |
| ------ | -------------------- | --------------------------- |
| POST   | `/api/filter-player` | Filtra jugadores del club   |
| POST   | `/api/delete-player` | Elimina un jugador del club |

### 🧬 Algoritmo genético

| Método | Endpoint             | Descripción             |
| ------ | -------------------- | ----------------------- |
| POST   | `/api/generate-team` | Genera plantilla óptima |

<img width="2556" height="1265" alt="image" src="https://github.com/user-attachments/assets/1255f5bd-bd9f-4e6f-9113-cf6fd0c670c1" />

Ejemplo de cuerpo de petición:

```json
{
  "sbcNumber": 3
}
```

## 🧬 Algoritmo genético

El motor de generación de plantillas se basa en un algoritmo genético que:

- Representa una plantilla como un cromosoma
- Evalúa soluciones mediante una función de aptitud
- Minimiza el coste total de la plantilla
- Penaliza el incumplimiento de requisitos del DCP
- Aplica operadores de selección, cruce y mutación
- Los hiperparámetros han sido ajustados experimentalmente durante el desarrollo del TFG.

## 🎥 Vídeo Divulgativo

El siguiente vídeo proporciona una idea general de los Desafios de Creación de Plantilla y de los Algoritmos Genéticos.

[![Ver demo del dashboard](https://img.youtube.com/vi/xlQMl1ehxoo/hqdefault.jpg)](https://www.youtube.com/watch?v=xlQMl1ehxoo)


## 📚 Contexto académico

Este backend forma parte del Trabajo de Fin de Grado del Grado en Ingeniería Informática
(Universitat de les Illes Balears, curso 2024–25).

**Autor**: Josep Gabriel Fornes Reynés
**Tutores**: Miquel Miró Nicolau, Javier Varona Gómez

El proyecto tiene finalidad exclusivamente académica, sin ánimo de lucro y respetando los Términos de Servicio de EA Sports FC 24.

## 🛑 Limitaciones

- No se integra con APIs oficiales de EA
- No realiza compra/venta automática de cartas
- Los precios no se actualizan en tiempo real
- Uso exclusivo en entorno de escritorio

## 🔮 Trabajo futuro

- Mejora del OCR en cartas especiales
- Optimización del algoritmo genético
- Soporte para nuevos tipos de DCP
- Paralelización del cálculo
- Persistencia histórica de resultados
