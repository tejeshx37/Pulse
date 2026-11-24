from unittest.mock import Mock, patch

import requests

from probe import check


def test_healthy_response():
    with patch("probe.requests.get", return_value=Mock(status_code=200)):
        ok, code, ms, err = check("http://example")
    assert ok is True
    assert code == 200
    assert err is None


def test_http_500_is_a_failure_with_label():
    with patch("probe.requests.get", return_value=Mock(status_code=500)):
        ok, code, ms, err = check("http://example")
    assert ok is False
    assert code == 500
    assert err == "HTTP 500"


def test_connection_error_is_a_failure():
    with patch("probe.requests.get", side_effect=requests.ConnectionError()):
        ok, code, ms, err = check("http://example")
    assert ok is False
    assert code is None
    assert err == "ConnectionError"
