
"""YouTube URL identification and public metadata utilities."""

import re
from urllib.parse import parse_qs, urlparse


VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")

ALLOWED_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtube-nocookie.com",
}


def extract_video_id(url: str) -> str:
    """Extract and validate an 11-character YouTube video ID."""

    if not isinstance(url, str) or not url.strip():
        raise ValueError("Please provide a YouTube URL.")

    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("The URL must use HTTP or HTTPS.")

    if host not in ALLOWED_HOSTS:
        raise ValueError("This is not a recognized YouTube domain.")

    video_id = None

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]

    elif parsed.path == "/watch":
        video_id = parse_qs(parsed.query).get("v", [None])[0]

    else:
        match = re.match(
            r"^/(?:shorts|embed|live)/([A-Za-z0-9_-]{11})",
            parsed.path,
        )

        if match:
            video_id = match.group(1)

    if not video_id or not VIDEO_ID_PATTERN.fullmatch(video_id):
        raise ValueError("Could not identify a valid YouTube video ID.")

    return video_id


def normalize_youtube_url(url: str) -> str:
    """Return a clean canonical YouTube URL."""

    video_id = extract_video_id(url)

    return f"https://www.youtube.com/watch?v={video_id}"
