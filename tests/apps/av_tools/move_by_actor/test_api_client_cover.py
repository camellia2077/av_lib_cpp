from apps.av_tools.move_by_actor.app.api_client import extract_cover_url, extract_tag_names


def test_extract_cover_url_from_direct_string() -> None:
    data = {"cover": "https://example.com/cover.jpg"}
    assert extract_cover_url(data) == "https://example.com/cover.jpg"


def test_extract_cover_url_from_nested_object() -> None:
    data = {"poster": {"src": "https://example.com/poster.png"}}
    assert extract_cover_url(data) == "https://example.com/poster.png"


def test_extract_cover_url_from_gallery_list() -> None:
    data = {"gallery": [{"url": "https://example.com/1.jpg"}]}
    assert extract_cover_url(data) == "https://example.com/1.jpg"


def test_extract_tag_names_from_genres_and_tags() -> None:
    data = {
        "genres": [{"name": "NTR"}, {"name": "Drama"}],
        "tags": ["ntr", "School"],
    }
    assert extract_tag_names(data) == ["NTR", "Drama", "School"]
