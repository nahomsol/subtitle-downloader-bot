import requests
import io

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


def download_subtitle(file_id):
    """Download subtitle file from OpenSubtitles API"""
    headers = {
        "Api-Key": OPENSUBTITLES_API_KEY,
        "User-Agent": "SubtitleDownloaderBot v1.0",
    }

    try:
        response = requests.get(
            f"{BASE_URL}/download",
            headers=headers,
            params={"file_id": file_id},
            timeout=20,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if "link" not in data:
            return None

        # Get download link from response
        download_link = data.get("link")

        # Download the actual subtitle file
        subtitle_response = requests.get(download_link, timeout=20)

        if subtitle_response.status_code != 200:
            return None

        # Return file as bytes
        return io.BytesIO(subtitle_response.content)

    except Exception as e:
        print(f"Error downloading subtitle: {e}")
        return None
