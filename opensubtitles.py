import requests

from config import OPENSUBTITLES_API_KEY

BASE_URL = "https://api.opensubtitles.com/api/v1"


def search_subtitles(imdb_id):
    headers = {
        "Api-Key": OPENSUBTITLES_API_KEY,
        "User-Agent": "SubtitleDownloaderBot v1.0",
    }

    params = {
        "imdb_id": imdb_id.replace("tt", ""),
    }

    response = requests.get(
        f"{BASE_URL}/subtitles",
        headers=headers,
        params=params,
        timeout=20,
    )

    if response.status_code != 200:
        return []

    data = response.json()

    subtitles = []

    for item in data.get("data", []):
        attributes = item.get("attributes", {})

        subtitles.append(
            {
                "language": attributes.get("language"),
                "download_count": attributes.get("download_count", 0),
                "file_id": attributes.get("files", [{}])[0].get("file_id"),
            }
        )

    return subtitles
