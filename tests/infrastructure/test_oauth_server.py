"""Tests for the OAuth callback server."""

import http.client

import pytest

from linkedin_mcp.infrastructure.oauth_server import OAuthCallbackServer, _OAuthCallbackHandler


def _get_free_port() -> int:
    """Find a free port to avoid conflicts."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", 0))
        return s.getsockname()[1]


def _send_callback(port: int, path: str) -> int:
    """Send an HTTP GET request to the callback server."""
    conn = http.client.HTTPConnection("localhost", port, timeout=5)
    conn.request("GET", path)
    resp = conn.getresponse()
    status = resp.status
    conn.close()
    return status


def test_redirect_uri_format() -> None:
    """redirect_uri should use the configured port."""
    server = OAuthCallbackServer(port=9999)
    assert server.redirect_uri == "http://localhost:9999/callback"


def test_is_waiting_before_start() -> None:
    """is_waiting should be False before start."""
    server = OAuthCallbackServer()
    assert server.is_waiting is False


def test_get_code_without_start_raises() -> None:
    """get_code should raise if start() wasn't called."""
    server = OAuthCallbackServer()
    with pytest.raises(RuntimeError, match="has not been started"):
        server.get_code()


def test_get_code_success() -> None:
    """get_code should return the authorization code from the callback."""
    port = _get_free_port()
    server = OAuthCallbackServer(port=port, timeout=10)
    server.start()

    assert server.is_waiting is True

    status = _send_callback(port, "/callback?code=test-auth-code&state=linkedin_mcp_auth")
    assert status == 200

    code = server.get_code(timeout=5)
    assert code == "test-auth-code"
    assert server.is_waiting is False


def test_get_code_with_error() -> None:
    """get_code should raise RuntimeError when callback has error."""
    port = _get_free_port()
    server = OAuthCallbackServer(port=port, timeout=10)
    server.start()

    status = _send_callback(port, "/callback?error=access_denied&error_description=user+denied")
    assert status == 400

    with pytest.raises(RuntimeError, match="authorization denied"):
        server.get_code(timeout=5)


def test_get_code_timeout() -> None:
    """get_code should raise TimeoutError when no callback arrives."""
    port = _get_free_port()
    server = OAuthCallbackServer(port=port, timeout=1)
    server.start()

    with pytest.raises(TimeoutError, match="Timed out"):
        server.get_code(timeout=1)


def test_start_twice_raises() -> None:
    """start() should raise if already running."""
    port = _get_free_port()
    server = OAuthCallbackServer(port=port, timeout=10)
    server.start()

    try:
        with pytest.raises(RuntimeError, match="already running"):
            server.start()
    finally:
        # Send a request to unblock the server thread
        try:
            _send_callback(port, "/callback?code=cleanup")
        except Exception:
            pass
        server.get_code(timeout=2)


def test_bad_request_without_code_or_error() -> None:
    """Server should return 400 for requests without code or error."""
    port = _get_free_port()
    server = OAuthCallbackServer(port=port, timeout=10)
    server.start()

    status = _send_callback(port, "/callback?unexpected=param")
    assert status == 400

    # Server handled one request and stopped; get_code should timeout
    with pytest.raises(TimeoutError):
        server.get_code(timeout=1)


def test_log_message_suppressed() -> None:
    """Handler log_message should be a no-op (no exception)."""
    handler = _OAuthCallbackHandler.__new__(_OAuthCallbackHandler)
    handler.log_message("test %s", "arg")
