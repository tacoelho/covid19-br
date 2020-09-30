from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import rows
from rows.utils import load_schema

DATA_PATH = Path(__file__).parent / "data"
SCHEMA_PATH = Path(__file__).parent / "schema"
POPULATION_DATA_PATH = {
    2019: DATA_PATH / "populacao-por-municipio-2019.csv",
    2020: DATA_PATH / "populacao-por-municipio-2020.csv",
}
POPULATION_SCHEMA_PATH = SCHEMA_PATH / "populacao-por-municipio.csv"


@lru_cache(maxsize=2)
def cities(year):
    table = rows.import_from_csv(POPULATION_DATA_PATH[year], force_types=load_schema(str(POPULATION_SCHEMA_PATH)),)
    cities = defaultdict(dict)
    for row in table:
        cities[row.state][row.city] = row
    return cities


@lru_cache(maxsize=5570)
def city_code(state, city, year=2020):
    return cities(year)[state][city].city_ibge_code


@lru_cache(maxsize=11140)
def city_population(state, city, year):
    return cities(year)[state][city].estimated_population


@lru_cache(maxsize=27)
def state_code(state, year=2020):
    for city in cities(year)[state].values():
        return city.state_ibge_code


@lru_cache(maxsize=54)
def state_population(state, year):
    return sum(city.estimated_population for city in cities(year)[state].values())


@lru_cache(maxsize=1)
def states(year=2020):
    return sorted(cities(year).keys())


@lru_cache(maxsize=2)
def place_keys(year=2020):
    """Cria chave única para cada tipo de local em que são contabilizados casos"""
    keys = Counter()
    for state, state_cities in cities(year).items():
        keys.append(("state", state, None))
        keys.append(("city", state, "Importados/Indefinidos"))
        for city_name in state_cities.keys():
            keys.append(("city", state, city_name))
    keys.sort()
    return keys
