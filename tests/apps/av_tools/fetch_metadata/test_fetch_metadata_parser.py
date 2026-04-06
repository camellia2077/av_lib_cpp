from apps.av_tools.fetch_metadata.parser import extract_standard_movie_code


def test_extract_standard_movie_code_accepts_structured_match() -> None:
    assert extract_standard_movie_code("SSIS-001 Amazing title") == "SSIS-001"


def test_extract_standard_movie_code_rejects_fallback() -> None:
    assert extract_standard_movie_code("just some title") is None


def test_extract_standard_movie_code_supports_vendor_rule() -> None:
    assert extract_standard_movie_code("heyzo_hd_0904_full") == "HEYZO-0904"


def test_extract_standard_movie_code_drops_split_part_suffix() -> None:
    assert extract_standard_movie_code("IPSD-048-A") == "IPSD-048"
    assert extract_standard_movie_code("MVSD-294-2") == "MVSD-294"
