import json
import os
import re
import easyocr
import pymysql
from pymysql.cursors import DictCursor

# Configuración de conexión a la base de datos
db_config = {
    'host': 'localhost',     # Cambiar si no es localhost
    'user': 'root',    # Usuario de la base de datos
    'password': 'root',  # Contraseña de la base de datos
    'database': 'fc24_futbinstats',  # Nombre de la base de datos
}

general_path = 'segmentations_YOLO'
name_path = f'{general_path}/name'
overall_path = f'{general_path}/overall'
position_path = f'{general_path}/position'
pace_path = f'{general_path}/pace'
shooting_path = f'{general_path}/shooting'
passing_path = f'{general_path}/passing'
dribbling_path = f'{general_path}/dribbling'
defending_path = f'{general_path}/defending'
phisicallity_path = f'{general_path}/phisicallity'
cards_path = f'{general_path}/cards'

def extract_number(filename):
    """
    Retorna el primer número (enter) que trobi en el nom del fitxer.
    Si no en troba cap, retorna 0.
    """
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 0

def get_images(folder):
    """
    Returns the list of image paths existing in the folder, sorted by the number extracted from the file name.
    """
    if not os.path.isdir(folder):
        print(f"The folder '{folder}' don't exist")
        return []

    # Obtenim tots els fitxers d'imatge
    images = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff"))
    ]

    # Ordenem pel número que aparegui al nom del fitxer
    # Exemple: name_2.png -> 2, name_10.png -> 10, etc.
    images.sort(key=lambda x: extract_number(os.path.basename(x)))
    return images

def verify_image_counts(folders):
    """
    Verifies if all folders have the same number of images.
    Prints a warning if the counts do not match.
    """
    # Get the number of images in each folder
    folder_image_counts = {folder: len(get_images(folder)) for folder in folders}

    # Check if all folders have the same number of images
    if len(set(folder_image_counts.values())) != 1:
        print("⚠️ Warning: The number of images in the folders does not match.")
        for folder, count in folder_image_counts.items():
            print(f"Folder '{folder}': {count} images.")
    else:
        print("✅ All folders have the same number of images.")

def process_image_data(reader, name_path, overall_path, position_path, pace_path, shooting_path, passing_path, dribbling_path, defending_path, physicallity_path):
    """
    Processes image data using OCR and extracts text and numeric values.

    Args:
        reader: The OCR reader instance.
        name_path: Path to the name image.
        overall_path: Path to the overall image.
        position_path: Path to the position image.
        pace_path: Path to the pace image.
        shooting_path: Path to the shooting image.
        passing_path: Path to the passing image.
        dribbling_path: Path to the dribbling image.
        defending_path: Path to the defending image.
        physicallity_path: Path to the physicallity image.

    Returns:
        A dictionary containing the extracted text and numeric values.
    """
    # Read the images
    name_result = reader.readtext(name_path)
    overall_result = reader.readtext(overall_path)
    position_result = reader.readtext(position_path)
    pace_result = reader.readtext(pace_path)
    shooting_result = reader.readtext(shooting_path)
    passing_result = reader.readtext(passing_path)
    dribbling_result = reader.readtext(dribbling_path)
    defending_result = reader.readtext(defending_path)
    physicallity_result = reader.readtext(physicallity_path)

    # Extract text safely
    name_text = name_result[0][1] if name_result else "Desconocido"
    overall_text = overall_result[0][1] if overall_result else "Desconocido"
    position_text = position_result[0][1] if position_result else "Desconocido"
    pace_text = pace_result[0][1] if pace_result else "Desconocido"
    shooting_text = shooting_result[0][1] if shooting_result else "Desconocido"
    passing_text = passing_result[0][1] if passing_result else "Desconocido"
    dribbling_text = dribbling_result[0][1] if dribbling_result else "Desconocido"
    defending_text = defending_result[0][1] if defending_result else "Desconocido"
    physicallity_text = physicallity_result[0][1] if physicallity_result else "Desconocido"

    # Convert text to numbers safely
    try:
        overall_value = int(overall_text)
    except ValueError:
        overall_value = None

    try:
        pace_value = int(pace_text)
    except ValueError:
        pace_value = None

    try:
        shooting_value = int(shooting_text)
    except ValueError:
        shooting_value = None

    try:
        passing_value = int(passing_text)
    except ValueError:
        passing_value = None

    try:
        dribbling_value = int(dribbling_text)
    except ValueError:
        dribbling_value = None

    try:
        defending_value = int(defending_text)
    except ValueError:
        defending_value = None

    try:
        physicallity_value = int(physicallity_text)
    except ValueError:
        physicallity_value = None

    return {
        "name": name_text,
        "overall": overall_value,
        "position": position_text,
        "pace": pace_value,
        "shooting": shooting_value,
        "passing": passing_value,
        "dribbling": dribbling_value,
        "defending": defending_value,
        "physicallity": physicallity_value
    }

def search_player_database(name, overall, position, pace, shooting, passing, dribbling, defending, physicallity):
    # Connect to the database
    try:
        connection = pymysql.connect(**db_config, cursorclass=DictCursor)
        cursor = connection.cursor()

        conditions = []

        if name != "Desconocido":
            # Dividir el nombre en palabras y construir condiciones LIKE
            words = name.split()
            name_conditions = " AND ".join([f"name LIKE '%{word}%'" for word in words])
            conditions.append(name_conditions)

        if overall is not None:
            conditions.append(f"rating = {overall}")

        # Unir las condiciones con AND
        if conditions:
            sql_conditions = " AND ".join(conditions)
            sql = f"SELECT * FROM players WHERE {sql_conditions};"
            cursor.execute(sql)
            results = cursor.fetchall()
        else:
            results = []  # No se ejecuta la consulta si no hay condiciones

        if len(results) == 0 or len(results) > 1:
            attributes = {
                "pace": pace,
                "shooting": shooting,
                "passing": passing,
                "dribbling": dribbling,
                "defending": defending,
                "physicality": physicallity
            }

            # Filtrar los atributos que no son None
            filtered_attributes = {key: value for key, value in attributes.items() if value is not None}

            # Construir las condiciones SQL dinámicamente
            conditions = " AND ".join([f"{key} = {value}" for key, value in filtered_attributes.items()])

            # Construir la consulta SQL
            sql = f"SELECT * FROM players WHERE {conditions};"

            cursor.execute(sql)
            results = cursor.fetchall() # agafam el primer, pero es possible que si feim un fetchall n'hi hagui més d'un

        return results

    except Exception as e:
        print(f"Error al conectar o buscar en la base de datos: {e}")
        return None

class Jugador:
    def __init__(self, name, rating, position, price, club, nacionality, league, version, pace, shooting, passing, dribbling, defending, phisicality, foot, weakFoot, skills, body, gender, image):
        self.name = name
        self.rating = rating
        self.nacionality = nacionality
        self.league = league
        self.club = club
        self.position = position
        self.version = version
        self.price = price
        self.pace = pace
        self.shooting = shooting
        self.passing = passing
        self.dribbling = dribbling
        self.defending = defending
        self.phisicality = phisicality
        self.foot = foot
        self.weakFoot = weakFoot
        self.skills = skills
        self.body = body
        self.gender = gender
        self.image = image

    def __str__(self):
        return f"Jugador({self.name}, {self.rating}, {self.nacionality}, {self.league}, {self.club}, {self.position}, {self.version}, {self.price}, {self.pace}, {self.shooting}, {self.passing}, {self.dribbling}, {self.defending}, {self.phisicality}, {self.foot}, {self.weakFoot}, {self.skills}, {self.body}, {self.gender}, {self.image})"

def normalize_positions(positions):
    """
    Normalizes the position string putting commas.
    """
    # Normalizar los espacios en resultado["pos"]
    normalized = re.sub(r'\s+', ',', positions)
    return normalized

def normalize_price(price):
    """
    Normalizes the price string by converting it to an integer value.
    Handles formats like '1.78M', '20.9K', and plain numbers.
    """
    try:
        # Remove commas for plain numbers
        price = price.replace(',', '')

        if 'M' in price:
            # Convert millions
            return int(float(price.replace('M', '')) * 1_000_000)
        elif 'K' in price:
            # Convert thousands
            return int(float(price.replace('K', '')) * 1_000)
        else:
            # Convert plain numbers
            return int(price)
    except ValueError:
        # Handle invalid price formats
        print(f"Invalid price format: {price}")
        return 0

def save_players(players):
    """
    Save the players data to a JSON file.
    """
    # Nombre del archivo donde guardar los datos
    archivo_json = "jugadores.json"

    # Guardar la lista de jugadores en un archivo JSON
    with open(archivo_json, 'w', encoding='utf-8') as f:
        json.dump([player.__dict__ for player in players], f, ensure_ascii=False, indent=4)