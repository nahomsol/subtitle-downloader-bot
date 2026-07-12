import requests

from config import TMDB_API_KEY

BASE_URL = "https://api.themoviedb.org/3"


def search_movie(query):
    url = f"{BASE_URL}/search/multi"

    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
    }

    response = requests.get(url, params=params, timeout=20)

    if response.status_code != 200:
        return None

    data = response.json()

    results = data.get("results", [])

    if not results:
        return None

    return results[0]


def get_imdb_id(media_type, tmdb_id):
    if media_type == "movie":
        url = f"{BASE_URL}/movie/{tmdb_id}/external_ids"
    elif media_type == "tv":
        url = f"{BASE_URL}/tv/{tmdb_id}/external_ids"
    else:
        return None

    params = {
        "api_key": TMDB_API_KEY
    }

    response = requests.get(url, params=params, timeout=20)

    if response.status_code != 200:
        return None

    data = response.json()

    return data.get("imdb_id")
