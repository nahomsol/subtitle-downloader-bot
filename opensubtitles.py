import requests
import io
import gzip

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
        "Accept-Encoding": "gzip, deflate",
    }

    try:
        response = requests.get(
            f"{BASE_URL}/download",
            headers=headers,
            params={"file_id": file_id},
            timeout=30,
        )

        print(f"Download response status: {response.status_code}")
        print(f"Download response headers: {response.headers}")

        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            return None

        data = response.json()
        print(f"Download response data: {data}")

        if "link" not in data:
            print("Error: No 'link' field in response")
            print(f"Available fields: {data.keys()}")
            return None

        # Get download link from response
        download_link = data.get("link")
        print(f"Download link: {download_link}")

        # Download the actual subtitle file
        subtitle_response = requests.get(download_link, timeout=30)

        print(f"Subtitle file response status: {subtitle_response.status_code}")

        if subtitle_response.status_code != 200:
            print(f"Error downloading file: Status {subtitle_response.status_code}")
            return None

        # Handle gzip compression if needed
        content = subtitle_response.content
        if subtitle_response.headers.get('content-encoding') == 'gzip':
            content = gzip.decompress(content)

        print(f"Subtitle file size: {len(content)} bytes")

        # Return file as bytes
        return io.BytesIO(content)

    except Exception as e:
        print(f"Error downloading subtitle: {e}")
        import traceback
        traceback.print_exc()
        return None
