"""Local OAuth callback server for capturing LinkedIn authorization codes."""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

_DEFAULT_PORT = 8099
_DEFAULT_TIMEOUT = 120


class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler that captures OAuth callback parameters."""

    authorization_code: str | None = None
    error: str | None = None

    def do_GET(self) -> None:
        """Handle the OAuth callback GET request."""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            _OAuthCallbackHandler.authorization_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authorization successful!</h1>"
                b"<p>You can close this window and return to your application.</p>"
                b"</body></html>"
            )
        elif "error" in params:
            _OAuthCallbackHandler.error = params.get("error_description", params["error"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authorization failed.</h1><p>Please try again.</p></body></html>"
            )
        else:
            self.send_response(400)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        """Suppress default HTTP server logging."""


class OAuthCallbackServer:
    """Starts a temporary local HTTP server to capture OAuth redirects.

    Listens on localhost for the LinkedIn OAuth callback, extracts the
    authorization code, then shuts down.
    """

    def __init__(self, port: int = _DEFAULT_PORT, timeout: int = _DEFAULT_TIMEOUT) -> None:
        """Initialize the callback server.

        Args:
            port: Port to listen on (default 8099).
            timeout: Seconds to wait before timeout (default 120).
        """
        self._port = port
        self._timeout = timeout
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    @property
    def redirect_uri(self) -> str:
        """Get the redirect URI for OAuth configuration.

        Returns:
            The localhost callback URL.
        """
        return f"http://localhost:{self._port}/callback"

    @property
    def is_waiting(self) -> bool:
        """Check if the server is currently waiting for a callback.

        Returns:
            True if the server is running and waiting.
        """
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        """Start the callback server in a background thread.

        The server listens for a single request and then stops.

        Raises:
            RuntimeError: If the server is already running.
        """
        if self.is_waiting:
            msg = "OAuth callback server is already running."
            raise RuntimeError(msg)

        _OAuthCallbackHandler.authorization_code = None
        _OAuthCallbackHandler.error = None

        self._server = HTTPServer(("localhost", self._port), _OAuthCallbackHandler)
        self._server.timeout = self._timeout

        def handle_request() -> None:
            if self._server is not None:
                self._server.handle_request()

        self._thread = threading.Thread(target=handle_request, daemon=True)
        self._thread.start()

    def get_code(self, timeout: float | None = None) -> str:
        """Wait for the authorization code from the callback.

        Must be called after ``start()``.

        Args:
            timeout: Seconds to wait. Defaults to the server's configured timeout.

        Returns:
            The authorization code from the callback.

        Raises:
            RuntimeError: If the server hasn't been started or user denied auth.
            TimeoutError: If no callback is received within the timeout.
        """
        if self._thread is None:
            msg = "OAuth callback server has not been started. Call start() first."
            raise RuntimeError(msg)

        wait = timeout if timeout is not None else self._timeout
        self._thread.join(timeout=wait)

        if self._server is not None:
            self._server.server_close()
            self._server = None
        self._thread = None

        if _OAuthCallbackHandler.error is not None:
            msg = f"LinkedIn authorization denied: {_OAuthCallbackHandler.error}"
            raise RuntimeError(msg)

        if _OAuthCallbackHandler.authorization_code is None:
            msg = "Timed out waiting for LinkedIn authorization callback."
            raise TimeoutError(msg)

        return _OAuthCallbackHandler.authorization_code
