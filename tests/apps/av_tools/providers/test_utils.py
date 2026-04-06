from apps.av_tools.providers.utils import Candidate, expand_query_keys, select_best_candidate


def test_expand_query_keys_includes_separator_variants() -> None:
    keys = expand_query_keys("IPSD-048")
    assert "IPSD-048" in keys
    assert "IPSD_048" in keys
    assert "IPSD048" in keys


def test_select_best_candidate_prefers_exact_normalized_code() -> None:
    target = "IPSD-048"
    candidates = [
        Candidate(code="IPSD-049", url="https://x/2"),
        Candidate(code="IPSD048", url="https://x/1"),
    ]
    chosen = select_best_candidate(target, candidates)
    assert chosen is not None
    assert chosen.url == "https://x/1"

