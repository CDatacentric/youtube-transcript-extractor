
"""Authorized YouTube caption retrieval.

Uses the official YouTube Data API.
The authenticated Google account must have permission
to manage captions for the requested video.
"""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

CREDENTIALS_FILE = Path("credentials.json")
TOKEN_FILE = Path("token.json")


def get_youtube_service():
    """Authenticate the user and create a YouTube API client."""

    credentials = None

    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SCOPES,
        )

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    if not credentials or not credentials.valid:

        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                "Google OAuth credentials.json was not found. "
                "Configure your Google Cloud OAuth application first."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            SCOPES,
        )

        credentials = flow.run_local_server(
            port=0,
            access_type="offline",
            prompt="consent",
        )

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    return build(
        "youtube",
        "v3",
        credentials=credentials,
        cache_discovery=False,
    )


def list_caption_tracks(video_id):
    """List caption tracks available to the authorized account."""

    service = get_youtube_service()

    response = service.captions().list(
        part="snippet",
        videoId=video_id,
    ).execute()

    tracks = []

    for item in response.get("items", []):
        snippet = item.get("snippet", {})

        tracks.append({
            "id": item["id"],
            "language": snippet.get("language", "unknown"),
            "name": snippet.get("name", ""),
            "track_kind": snippet.get("trackKind", "standard"),
            "is_draft": snippet.get("isDraft", False),
            "status": snippet.get("status", "unknown"),
        })

    return tracks


def download_caption_track(caption_id):
    """Download a caption track in WebVTT format."""

    service = get_youtube_service()

    content = service.captions().download(
        id=caption_id,
        tfmt="vtt",
    ).execute()

    if isinstance(content, bytes):
        return content.decode("utf-8-sig")

    return str(content)


def parse_webvtt(content):
    """Convert WebVTT caption content into timestamped segments."""

    import re

    segments = []

    blocks = re.split(r"\n\s*\n", content.strip())

    for block in blocks:
        lines = block.strip().splitlines()

        timestamp_index = next(
            (
                i for i, line in enumerate(lines)
                if "-->" in line
            ),
            None,
        )

        if timestamp_index is None:
            continue

        timestamp_line = lines[timestamp_index]

        match = re.match(
            r"(\d{2}:)?(\d{2}:\d{2}\.\d{3})\s+-->",
            timestamp_line,
        )

        if not match:
            continue

        timestamp = match.group(1) or "00:"
        timestamp += match.group(2)

        text_lines = lines[timestamp_index + 1:]

        text = " ".join(text_lines)

        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text).strip()

        if text:
            segments.append({
                "timestamp": timestamp,
                "text": text,
            })

    return segments
