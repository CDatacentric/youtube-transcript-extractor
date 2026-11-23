
"""Central manager for available transcription engines."""

from engines.youtube_engine import extract_video_id
from engines.caption_engine import (
    list_caption_tracks,
    download_caption_track,
    parse_webvtt,
)


class TranscriptionError(Exception):
    """Raised when a transcript cannot be retrieved."""


def select_caption_track(tracks, preferred_language=None):
    """Choose the best available caption track."""

    if not tracks:
        return None

    usable_tracks = [
        track for track in tracks
        if not track.get("is_draft", False)
    ]

    if not usable_tracks:
        return None

    if preferred_language:
        matching = [
            track for track in usable_tracks
            if track.get("language") == preferred_language
        ]

        if matching:
            return matching[0]

    # Prefer manually created captions over automatic captions.
    manual_tracks = [
        track for track in usable_tracks
        if track.get("track_kind") != "ASR"
    ]

    if manual_tracks:
        return manual_tracks[0]

    return usable_tracks[0]


def extract_youtube_transcript(url, preferred_language=None):
    """Retrieve captions accessible to the authenticated account."""

    try:
        video_id = extract_video_id(url)

        tracks = list_caption_tracks(video_id)

        if not tracks:
            raise TranscriptionError(
                "No caption tracks are available to your "
                "authorized YouTube account."
            )

        selected_track = select_caption_track(
            tracks,
            preferred_language,
        )

        if selected_track is None:
            raise TranscriptionError(
                "No usable caption track was found."
            )

        content = download_caption_track(
            selected_track["id"]
        )

        segments = parse_webvtt(content)

        if not segments:
            raise TranscriptionError(
                "The caption file contained no readable transcript."
            )

        return {
            "success": True,
            "video_id": video_id,
            "language": selected_track["language"],
            "source": "youtube_authorized_captions",
            "track_kind": selected_track["track_kind"],
            "segments": segments,
            "segment_count": len(segments),
            "status": "retrieved",
        }

    except TranscriptionError:
        raise

    except Exception as error:
        raise TranscriptionError(
            f"YouTube transcript retrieval failed: {error}"
        ) from error
