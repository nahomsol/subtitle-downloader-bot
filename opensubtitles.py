import requests
import os

API_KEY = os.getenv("OPENSUBTITLES_API_KEY")

HEADERS = {
    "Api-Key": API_KEY,
    "Content-Type": "application/json"
}


def search_subtitles(imdb_id):
    url = "https://api.opensubtitles.com/api/v1/subtitles"

    params = {
        "parent_imdb_id": imdb_id,
        "languages": "en"
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params
    )

    data = response.json()

    results = []

    for item in data.get("data", []):
        attr = item.get("attributes", {})

        results.append({
            "id": item.get("id"),
            "language": attr.get("language"),
            "release": attr.get("release")
        })

    return results


def download_subtitle(file_id):
    url = "https://api.opensubtitles.com/api/v1/download"

    response = requests.post(
        url,
        headers=HEADERS,
        json={"file_id": file_id}
    )

    return response.json()
