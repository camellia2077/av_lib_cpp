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


def test_extract_standard_movie_code_drops_vendor_suffix_for_uncensored() -> None:
    assert extract_standard_movie_code("031315-827-carib") == "031315-827"
    assert extract_standard_movie_code("091416_382-1pondo") == "091416_382"


def test_extract_standard_movie_code_keeps_vendor_canonical_ids() -> None:
    assert extract_standard_movie_code("heyzo_hd_0904_full") == "HEYZO-0904"
    assert extract_standard_movie_code("n1039_kaori_shiraishi_eb_n_fhd") == "TOKYO-HOT-N1039"
