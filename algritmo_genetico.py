import random
import json
import math
import pymysql
from pymysql.cursors import DictCursor

# Cargar jugadores desde un archivo JSON
with open("jugadores.json", "r", encoding='utf-8') as file:
    players_db = json.load(file)

# Cargar los requisitos desde un archivo JSON
with open("sbc.json", "r", encoding='utf-8') as file:
    requirements_data = json.load(file)

# Parámetros del algoritmo genético
num_players = len(players_db)
NUM_GENERATIONS = 800
POPULATION_SIZE = 200
MUTATION_RATE = 0.15
CROSSOVER_RATE = 0.25

def max_team_price(players_db):
    # Ordenar los jugadores por precio de mayor a menor
    sorted_players = sorted(players_db, key=lambda x: x['price'], reverse=True)

    # Seleccionar los 11 primeros jugadores
    top_11_players = sorted_players[:11]

    # Sumar los precios de los 11 primeros jugadores
    return sum(player['price'] for player in top_11_players)

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

def max_team_price_db(connection):
    """
    Calculates the maximum price of a team by selecting the 11 most expensive players
    whose price is in millions. Normalizes the price using the normalize_price function.
    """
    query = """
    SELECT price
    FROM players
    WHERE price LIKE '%M%'
    ORDER BY price DESC
    LIMIT 11;
    """
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    # Normalize and sum the prices
    total_price = sum(normalize_price(row['price']) for row in results)
    return total_price


def min_team_price(players_db):
    # Filter out players with invalid or missing 'price' values
    valid_players = [player for player in players_db if 'price' in player and isinstance(player['price'], (int, float))]

    # Sort the players by price from lowest to highest
    sorted_players = sorted(valid_players, key=lambda x: x['price'])

    # Select the first 11 players
    top_11_players = sorted_players[:11]

    # Sum the prices of the first 11 players
    return sum(player['price'] for player in top_11_players)

# Configuración de conexión a la base de datos
db_config = {
    'host': 'localhost',     # Cambiar si no es localhost
    'user': 'root',    # Usuario de la base de datos
    'password': 'root',  # Contraseña de la base de datos
    'database': 'fc24_futbinstats',  # Nombre de la base de datos
}

connection = pymysql.connect(**db_config, cursorclass=DictCursor)

#MAX_TEAM_PRICE = 1000000
#MAX_TEAM_PRICE = max_team_price_db(connection)
MAX_TEAM_PRICE = max_team_price(players_db)
MIN_TEAM_PRICE = min_team_price(players_db)

# Generar un equipo aleatorio permitiendo cualquier jugador en cualquier posición
def generate_random_team(positions):
    team = []
    selected_players = set()

    for position in positions:
        # diff = players_db - selected_players
        while True:
            random_player = random.choice(players_db)
            if random_player["name"] not in selected_players:
                selected_players.add(random_player["name"])
                team.append({"player": random_player, "assigned_position": position})
                break

    return team

def calculate_info(team):
    team_info = {
        "ratings": {},
        "nationalities": {},
        "leagues": {},
        "clubs": {},
        "versions": {},
        "nationalities_chemistry": {},
        "leagues_chemistry": {},
        "clubs_chemistry": {},
        "overall": 0,
        "overall_rounded": 0,
        "team_price": 0,
        "team_chemistry": 0,
        "players_chemistry": [],
        "players": 0,
    }
    for player in team:
        puntuacio = player["player"]["rating"]
        if puntuacio in team_info["ratings"]:
            team_info["ratings"][puntuacio] += 1
        else:
            team_info["ratings"][puntuacio] = 1

        nationality = player["player"]["nacionality"]
        if nationality in team_info["nationalities"]:
            team_info["nationalities"][nationality] += 1
        else:
            team_info["nationalities"][nationality] = 1

        league = player["player"]["league"]
        if league in team_info["leagues"]:
            team_info["leagues"][league] += 1
        else:
            team_info["leagues"][league] = 1

        club = player["player"]["club"]
        if club in team_info["clubs"]:
            team_info["clubs"][club] += 1
        else:
            team_info["clubs"][club] = 1

        version = player["player"]["version"]
        if version in team_info["versions"]:
            team_info["versions"][version] += 1
        else:
            team_info["versions"][version] = 1

        if player["assigned_position"] in player["player"]["position"].split(","):
            nationality_chemistry = player["player"]["nacionality"]
            if nationality_chemistry in team_info["nationalities_chemistry"]:
                team_info["nationalities_chemistry"][nationality_chemistry] += 1
            else:
                team_info["nationalities_chemistry"][nationality_chemistry] = 1

            league_chemistry = player["player"]["league"]
            if league_chemistry in team_info["leagues_chemistry"]:
                team_info["leagues_chemistry"][league_chemistry] += 1
            else:
                team_info["leagues_chemistry"][league_chemistry] = 1

            club_chemistry = player["player"]["club"]
            if club_chemistry in team_info["clubs_chemistry"]:
                team_info["clubs_chemistry"][club_chemistry] += 1
            else:
                team_info["clubs_chemistry"][club_chemistry] = 1

        team_info["overall"] = calculate_team_average_from_info(team_info)
        team_info["overall_rounded"] = math.floor(team_info["overall"])

        team_info["team_price"] += player["player"]["price"]

        team_info["players"] += 1

    team_chemistry = 0

    # Calculamos la quimica suplementaria de los iconos
    for player in team:
        if "Icon" in player["player"]["version"]:
            if player["assigned_position"] in player["player"]["position"].split(","):
                team_info["nationalities_chemistry"][player["player"]["nacionality"]] += 1
                for league in team_info["leagues"]:
                    if league not in team_info["leagues_chemistry"]:
                        team_info["leagues_chemistry"][league] = 1
                    else:
                        team_info["leagues_chemistry"][league] += 1

    # Calculamos la quimica suplementaria de los heroes
    for player in team:
        if "Hero" in player["player"]["version"]:
            if player["assigned_position"] in player["player"]["position"].split(","):
                team_info["leagues_chemistry"][player["player"]["league"]] += 1

    for player in team:
        player_chemistry = calculate_player_chemistry(player["player"], team_info, player["assigned_position"])
        team_chemistry += player_chemistry
        team_info["players_chemistry"].append({
            "player_name": player["player"]["name"],
            "chemistry": player_chemistry
        })

    team_info["team_chemistry"] = team_chemistry

    return team_info

def calculate_fitness(team_info, requirements):
    """
    Calculates the fitness of a team based on its compliance with specific requirements
    and adjusts the score according to the team's cost.

    Parameters:
    - team_info (dict): Contains 'overall_rounded', 'overall', and 'team_price'.
    - requirements (dict): Contains 'average' with possible 'min' value.

    Returns:
    - float: Fitness score of the team.
    """
    requirement_score = 0
    unmet_requirements = 0
    PENALTY_PER_UNMET_REQUIREMENT = 0.5

    # Comprobación del requisito de media mínima
    average_req = requirements.get("average", {})
    chemistry_req = requirements.get("chemistry", {})
    nationalities_req = requirements.get("nationalities", {})
    clubs_req = requirements.get("clubs", {})
    league_req = requirements.get("leagues", {})
    versions_req = requirements.get("versions", {})
    min_avg = average_req.get("min")
    min_chem = chemistry_req.get("min")
    max_chem = chemistry_req.get("max")
    player_min_chem = chemistry_req.get("player_min")
    player_max_chem = chemistry_req.get("player_max")
    min_nationalities = nationalities_req.get("min")
    max_nationalities = nationalities_req.get("max")
    exact_nationalities = nationalities_req.get("exact")
    player_min_nationalities = nationalities_req.get("player_min")
    player_max_nationalities = nationalities_req.get("player_max")
    min_clubs = clubs_req.get("min")
    max_clubs = clubs_req.get("max")
    exact_clubs = clubs_req.get("exact")
    player_min_clubs = clubs_req.get("player_min")
    player_max_clubs = clubs_req.get("player_max")
    min_leagues = league_req.get("min")
    max_leagues = league_req.get("max")
    exact_leagues = league_req.get("exact")
    player_min_leagues = league_req.get("player_min")
    player_max_leagues = league_req.get("player_max")
    min_versions = versions_req.get("min")
    max_versions = versions_req.get("max")

    if min_avg is not None:
        score = division_score(team_info["overall"], min_avg)
        requirement_score += score
        if team_info["overall"] < min_avg:
            unmet_requirements += 1

    if min_chem is not None:
        if team_info["team_chemistry"] < min_chem:
            unmet_requirements += 1
            score = division_score(team_info["team_chemistry"], min_chem)
            requirement_score += score

    if max_chem is not None:
        if team_info["team_chemistry"] > max_chem:
            unmet_requirements += 1
            score = division_score(team_info["team_chemistry"], max_chem)
            requirement_score += score

    if player_min_chem is not None:
        unmet_flag = False  # Flag to track if any player fails
        for player in team_info["players_chemistry"]:
            if player["chemistry"] < player_min_chem:
                score = division_score(player["chemistry"], player_min_chem)
                requirement_score += score
                unmet_flag = True  # Set the flag if a player fails
        if unmet_flag:
            unmet_requirements += 1  # Increment unmet_requirements only once

    if player_max_chem is not None:
        unmet_flag = False
        for player in team_info["players_chemistry"]:
            if player["chemistry"] > player_max_chem:
                score = division_score(player["chemistry"], player_max_chem)
                requirement_score += score
                unmet_flag = True
        if unmet_flag:
            unmet_requirements += 1

    if min_nationalities is not None:
        for nationality in min_nationalities:
            name = nationality["name"]
            number = nationality["number"]
            if team_info["nationalities"].get(name, 0) < number:
                unmet_requirements += 1
                score = division_score(team_info["nationalities"].get(name, 0), number)
                requirement_score += score

    if max_nationalities is not None:
        for nationality in max_nationalities:
            name = nationality["name"]
            number = nationality["number"]
            if team_info["nationalities"].get(name, 0) > number:
                unmet_requirements += 1
                score = division_score(team_info["nationalities"].get(name, 0), number)
                requirement_score += score

    if exact_nationalities is not None:
        if len(team_info["nationalities"]) != exact_nationalities:
            unmet_requirements += 1
            score = division_score(len(team_info["nationalities"]), exact_nationalities)
            requirement_score += score

    if player_min_nationalities is not None:
        unmet_flag = False
        for nationalities in team_info["nationalities"]:
            if team_info["nationalities"][nationalities] < player_min_nationalities:
                score = division_score(team_info["nationalities"][nationalities], player_min_nationalities)
                requirement_score += score
                unmet_flag = True
        if unmet_flag:
            unmet_requirements += 1

    if player_max_nationalities is not None:
        unmet_flag = False
        for nationalities in team_info["nationalities"]:
            if team_info["nationalities"][nationalities] > player_max_nationalities:
                score = division_score(team_info["nationalities"][nationalities], player_max_nationalities)
                requirement_score += score
                unmet_flag = True
        if unmet_flag:
            unmet_requirements += 1

    if min_clubs is not None:
        for club in min_clubs:
            name = club["name"]
            number = club["number"]
            if team_info["clubs"].get(name, 0) < number:
                unmet_requirements += 1
                score = division_score(team_info["clubs"].get(name, 0), number)
                requirement_score += score

    if max_clubs is not None:
        for club in max_clubs:
            name = club["name"]
            number = club["number"]
            if team_info["clubs"].get(name, 0) > number:
                unmet_requirements += 1
                score = division_score(team_info["clubs"].get(name, 0), number)
                requirement_score += score

    if exact_clubs is not None:
        if len(team_info["clubs"]) != exact_clubs:
            unmet_requirements += 1
            score = division_score(len(team_info["clubs"]), exact_clubs)
            requirement_score += score

    if player_min_clubs is not None:
        unmet_flag = False
        for clubs in team_info["clubs"]:
            if team_info["clubs"][clubs] < player_min_clubs:
                score = division_score(team_info["clubs"][clubs], player_min_clubs)
                requirement_score += score
                unmet_flag = True
        if unmet_flag:
            unmet_requirements += 1

    if player_max_clubs is not None:
        unmet_flag = False
        for clubs in team_info["clubs"]:
            if team_info["clubs"][clubs] > player_max_clubs:
                score = division_score(team_info["clubs"][clubs], player_max_clubs)
                requirement_score += score
                unmet_flag = True
        if unmet_flag:
            unmet_requirements += 1

    if min_leagues is not None:
        for league in min_leagues:
            name = league["name"]
            number = league["number"]
            if team_info["leagues"].get(name, 0) < number:
                unmet_requirements += 1
                score = division_score(team_info["leagues"].get(name, 0), number)
                requirement_score += score

    if max_leagues is not None:
        for league in max_leagues:
            name = league["name"]
            number = league["number"]
            if team_info["leagues"].get(name, 0) > number:
                unmet_requirements += 1
                score = division_score(team_info["leagues"].get(name, 0), number)
                requirement_score += score

    if exact_leagues is not None:
        if len(team_info["leagues"]) != exact_leagues:
            unmet_requirements += 1
            score = division_score(len(team_info["leagues"]), exact_leagues)
            requirement_score += score

    if player_min_leagues is not None:
        unmet_flag = False
        for leagues in team_info["leagues"]:
            if team_info["leagues"][leagues] < player_min_leagues:
                score = division_score(team_info["leagues"][leagues], player_min_leagues)
                requirement_score += score
                unmet_flag = True
        if unmet_flag:
            unmet_requirements += 1

    if player_max_leagues is not None:
        unmet_flag = False
        for leagues in team_info["leagues"]:
            if team_info["leagues"][leagues] > player_max_leagues:
                score = division_score(team_info["leagues"][leagues], player_max_leagues)
                requirement_score += score
                unmet_flag = True
        if unmet_flag:
            unmet_requirements += 1

    if min_versions is not None:
        for version in min_versions:
            name = version["name"]
            number = version["number"]
            count = sum(1 for v in team_info["versions"] if name in v)
            if count < number:
                unmet_requirements += 1
                score = division_score(count, number)
                requirement_score += score

    if max_versions is not None:
        for version in max_versions:
            name = version["name"]
            number = version["number"]
            count = sum(1 for v in team_info["versions"] if name in v)
            if count > number:
                unmet_requirements += 1
                score = division_score(count, number)
                requirement_score += score

    # Normalizar el costo del equipo para que tenga un peso similar al cambio de puntuación
    normalized_cost = normalize_team_price(team_info["team_price"], MIN_TEAM_PRICE, MAX_TEAM_PRICE)
    requirement_score += normalized_cost

    # Añadir penalización basada en el número de requisitos no cumplidos
    requirement_score += unmet_requirements * PENALTY_PER_UNMET_REQUIREMENT

    return requirement_score

def division_score(value, reference):
    """
    Returns the absolute value of the division between value and reference.

    Parameters:
    - value (float): Actual value.
    - reference (float): Reference value.

    Returns:
    - float: abs(value / reference)
    """
    if reference == 0:
        return 0  # evitar división por cero
    division = value / reference
    return abs(division - 1)

def normalize_team_price(team_price, min_price, max_price):
    """
    Normalizes the team price using min-max scaling between 0 and 1.

    Parameters:
    - team_price (float): The price of the team to normalize.
    - min_price (float): The minimum price in the data.
    - max_price (float): The maximum price in the data.

    Returns:
    - float: The normalized team price between 0 and 1.
    """
    if max_price == min_price:
        return 0  # Avoid division by zero if all prices are the same
    return (team_price - min_price) / (max_price - min_price)

# Aplicar la función de fitness a cada equipo en la población
def evaluate_population(population, requirements):
    team_scores = []
    for team in population:
        team_info = calculate_info(team)
        fitness = calculate_fitness(team_info, requirements)
        team_scores.append((team, team_info, fitness))

    return sorted(team_scores, key=lambda x: x[2])  # Ordenamos de mejor a peor fitness (menor a mayor)

def calculate_team_average_from_info(team_info):
    total_puntuation = sum(int(score) * count for score, count in team_info["ratings"].items())
    num_players = sum(team_info["ratings"].values())
    average_puntuation = total_puntuation / num_players

    excess_sum = sum((int(score) - average_puntuation) * count for score, count in team_info["ratings"].items() if int(score) > average_puntuation)

    adjusted_total = total_puntuation + excess_sum
    team_average = adjusted_total / num_players

    return team_average

def calculate_chemistry_points(count, thresholds):
    points = 0
    for threshold, point in thresholds:
        if count >= threshold:
            points = point
        else:
            break
    return points

club_thresholds = [(2, 1), (4, 2), (7, 3)]
league_thresholds = [(3, 1), (5, 2), (8, 3)]
nationality_thresholds = [(2, 1), (5, 2), (8, 3)]

def calculate_player_chemistry(player, team_info, assigned_position):
    if assigned_position not in player["position"].split(","):
        return 0

    if "Icon" in player["version"] or "Hero" in player["version"]:
        return 3

    club_points = calculate_chemistry_points(team_info["clubs_chemistry"][player["club"]], club_thresholds)
    league_points = calculate_chemistry_points(team_info["leagues_chemistry"][player["league"]], league_thresholds)
    nationality_points = calculate_chemistry_points(team_info["nationalities_chemistry"][player["nacionality"]], nationality_thresholds)

    player_chemistry = club_points + league_points + nationality_points

    if player_chemistry > 3:
        player_chemistry = 3

    return player_chemistry

def crossover(parent1, parent2):
    child = []
    selected_players = set()
    length = min(len(parent1), len(parent2))  # Ensure both parents have the same length
    for i in range(length):
        if random.random() > CROSSOVER_RATE and parent1[i]['player']['name'] not in selected_players:
            child.append(parent1[i])
            selected_players.add(parent1[i]['player']['name'])
        elif parent2[i]['player']['name'] not in selected_players:
            child.append(parent2[i])
            selected_players.add(parent2[i]['player']['name'])
        else:
            # If both players are already selected, choose a new random player
            while True:
                random_player = random.choice(players_db)
                if random_player['name'] not in selected_players:
                    child.append({'player': random_player, 'assigned_position': parent1[i]['assigned_position']})
                    selected_players.add(random_player['name'])
                    break
    return child

def mutate(team):
    selected_players = {player['player']['name'] for player in team}
    if random.random() < MUTATION_RATE:
        pos_to_mutate = random.randint(0, len(team) - 1)
        while True:
            new_player = random.choice(players_db)
            if new_player['name'] not in selected_players:
                team[pos_to_mutate] = {'player': new_player, 'assigned_position': team[pos_to_mutate]['assigned_position']}
                break
    return team


# Algoritmo Genético
def genetic_algorithm(team_requirements):
    positions = team_requirements['positions']
    requirements = team_requirements['requirements']
    population = [generate_random_team(positions) for _ in range(POPULATION_SIZE)]

    for generation in range(NUM_GENERATIONS):
        population = evaluate_population(population, requirements)
        new_population = [team for team, _, _ in population[:10]]  # Elitismo: mantener los mejores 10 equipos
        while len(new_population) < POPULATION_SIZE:
            parent1 = random.choice(population)[0]
            parent2 = random.choice(population)[0]
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)
        population = new_population

    best_teams = evaluate_population(population, requirements)
    print("Mejor equipo basado en menor precio y requisitos:")
    print(json.dumps(best_teams[0], ensure_ascii=False, indent=4))
    return best_teams[0]