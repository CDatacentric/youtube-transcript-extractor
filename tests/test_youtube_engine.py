
import pytest

from engines.youtube_engine import (
    extract_video_id,
    normalize_youtube_url,
)


def test_standard_youtube_url():
    url = "https://www.youtube.com/watch?v=abcdefghijk"
    assert extract_video_id(url) == "abcdefghijk"


def test_short_youtube_url():
    url = "https://youtu.be/abcdefghijk"
    assert extract_video_id(url) == "abcdefghijk"


def test_shorts_url():
    url = "https://www.youtube.com/shorts/abcdefghijk"
    assert extract_video_id(url) == "abcdefghijk"


def test_normalize_url():
    url = "https://youtu.be/abcdefghijk"
    assert normalize_youtube_url(url) == (
        "https://www.youtube.com/watch?v=abcdefghijk"
    )


def test_invalid_domain():
    with pytest.raises(ValueError):
        extract_video_id("https://example.com/abcdefghijk")


def test_empty_url():
    with pytest.raises(ValueError):
        extract_video_id("")
