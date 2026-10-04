from briefing.dedupe import key_for, normalize_url


def test_strips_tracking_params_and_sorts_query():
    url = "http://Example.com/post/?utm_source=x&b=2&fbclid=abc&a=1#frag"
    assert normalize_url(url) == "https://example.com/post?a=1&b=2"


def test_equivalent_urls_share_a_key():
    assert key_for("https://example.com/a/") == key_for("http://EXAMPLE.com/a?utm_medium=rss")


def test_root_path_kept():
    assert normalize_url("https://example.com") == "https://example.com/"


def test_distinct_urls_differ():
    assert key_for("https://example.com/a") != key_for("https://example.com/b")
