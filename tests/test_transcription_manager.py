
from unittest.mock import patch

import pytest

from engines.transcription_manager import (
    TranscriptionError,
    select_caption_track,
    extract_youtube_transcript,
)


def sample_tracks():
    return [
        {
            "id": "caption1",
            "language": "en",
            "track_kind": "ASR",
            "is_draft": False,
        },
        {
            "id": "caption2",
            "language": "fr",
            "track_kind": "standard",
            "is_draft": False,
        },
    ]


def test_select_preferred_language():
    result = select_caption_track(
        sample_tracks(),
        "fr",
    )

    assert result["id"] == "caption2"


def test_prefer_manual_captions():
    result = select_caption_track(sample_tracks())

    assert result["track_kind"] == "standard"


def test_no_tracks():
    assert select_caption_track([]) is None


@patch(
    "engines.transcription_manager.download_caption_track"
)
@patch(
    "engines.transcription_manager.list_caption_tracks"
)
def test_successful_transcript(mock_tracks, mock_download):

    mock_tracks.return_value = sample_tracks()

    mock_download.return_value = """WEBVTT

00:00:00.000 --> 00:00:03.000
Hello and welcome.
"""

    result = extract_youtube_transcript(
        "https://youtu.be/abcdefghijk",
        "en",
    )

    assert result["success"] is True
    assert result["video_id"] == "abcdefghijk"
    assert result["segment_count"] == 1
    assert result["language"] == "en"


@patch(
    "engines.transcription_manager.list_caption_tracks"
)
def test_unavailable_captions(mock_tracks):

    mock_tracks.return_value = []

    with pytest.raises(TranscriptionError):
        extract_youtube_transcript(
            "https://youtu.be/abcdefghijk"
        )
