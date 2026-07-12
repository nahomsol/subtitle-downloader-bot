import requests
import io
import gzip

from config import (
    OPENSUBTITLES_API_KEY,
    OPENSUBTITLES_USERNAME,
    OPENSUBTITLES_PASSWORD,
)

BASE_URL = "https://api.opensubtitles.com/api/v1"


def search_subtitles(imdb_id):
    """Search for subtitles by IMDb ID"""
    headers = {
        "Api-Key": OPENSUBTITLES_API_KEY,
        "User-Agent": "SubtitleDownloaderBot v1.0",
    }

    # Remove "tt" prefix if present, keep only numbers
    imdb_id_clean = imdb_id.replace("tt", "") if imdb_id.startswith("tt") else imdb_id

    params = {
        "imdb_id": imdb_id_clean,
    }

    try:
        print(f"Searching subtitles for IMDb ID: {imdb_id_clean}", flush=True)
        
        # Use GET to /search endpoint (not POST to /download)
        response = requests.get(
            f"{BASE_URL}/search",
            headers=headers,
            params=params,
            timeout=30,
        )

        print(f"Search response status: {response.status_code}", flush=True)

        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}", flush=True)
            print(f"Response: {response.text[:500]}", flush=True)
            return []

        data = response.json()
        print(f"Found response data with {len(data.get('data', []))} items", flush=True)

        subtitles = []

        for item in data.get("data", []):
            attributes = item.get("attributes", {})
            
            # Get file_id from files array
            files = attributes.get("files", [])
            if not files:
                continue
                
            file_id = files[0].get("file_id")
            if not file_id:
                continue

            subtitle_entry = {
                "language": attributes.get("language"),
                "file_id": file_id,
            }
            
            # Add optional fields if available (for display in keyboard)
            if attributes.get("release"):
                subtitle_entry["release"] = attributes.get("release")
            if attributes.get("release_name"):
                subtitle_entry["release_name"] = attributes.get("release_name")

            subtitles.append(subtitle_entry)

        print(f"Returning {len(subtitles)} subtitles", flush=True)
        return subtitles

    except Exception as e:
        print(f"Error searching subtitles: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return []


def download_subtitle(file_id):
    """Download subtitle file from OpenSubtitles API"""
    headers = {
        "Api-Key": OPENSUBTITLES_API_KEY,
        "User-Agent": "SubtitleDownloaderBot v1.0",
        "Accept-Encoding": "gzip, deflate",
    }

    try:
        print(f"Requesting download for file_id: {file_id}")
        
        response = requests.get(
            f"{BASE_URL}/download",
            headers=headers,
            params={"file_id": file_id},
            timeout=30,
        )

        print(f"Download response status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")

        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            return None

        # Check if response is actually JSON
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
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
                try:
                    content = gzip.decompress(content)
                except Exception as e:
                    print(f"Error decompressing gzip: {e}")

            print(f"Subtitle file size: {len(content)} bytes")
            return io.BytesIO(content)
        
        elif 'text/plain' in content_type or 'text/vtt' in content_type or 'application/x-subrip' in content_type:
            # Direct subtitle file response
            print("Received direct subtitle file")
            content = response.content
            
            if response.headers.get('content-encoding') == 'gzip':
                try:
                    content = gzip.decompress(content)
                except Exception as e:
                    print(f"Error decompressing gzip: {e}")
            
            print(f"Subtitle file size: {len(content)} bytes")
            return io.BytesIO(content)
        
        else:
            print(f"Unexpected content type: {content_type}")
            print(f"Response preview: {response.text[:500]}")
            return None

    except Exception as e:
        print(f"Error downloading subtitle: {e}")
        import traceback
        traceback.print_exc()
        return None
