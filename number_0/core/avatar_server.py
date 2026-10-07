"""
Локальный HTTP-сервер для аватара (обход CORS file://).
"""
import os
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from number_nol.core.logger import log


class _AvatarHandler(BaseHTTPRequestHandler):
    assets_dir: str = ""

    def log_message(self, format, *args):
        pass

    def _send(self, data: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _send_file(self, path: str, content_type: str) -> None:
        try:
            with open(path, "rb") as f:
                data = f.read()
        except FileNotFoundError:
            self.send_error(404, "Not Found")
            return
        self._send(data, content_type)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]

        if path in ("/", "/index.html", "/legion_avatar.html"):
            self._send_file(
                os.path.join(self.assets_dir, "legion_avatar.html"),
                "text/html; charset=utf-8",
            )
            return

        if path == "/avatar_state.json":
            state_path = os.path.join(self.assets_dir, "avatar_state.json")
            if not os.path.exists(state_path):
                data = json.dumps(
                    {"state": "idle", "text": ""}, ensure_ascii=False
                ).encode("utf-8")
                self._send(data, "application/json; charset=utf-8")
                return
            self._send_file(state_path, "application/json; charset=utf-8")
            return

        self.send_error(404, "Not Found")


class AvatarServer:

    def __init__(self, assets_dir: str, host: str = "127.0.0.1", port: int = 8765):
        self.assets_dir = os.path.abspath(assets_dir)
        self.host = host
        self.port = port
        self._httpd = None
        self._thread = None

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}/"

    def start(self) -> None:
        if self._httpd is not None:
            return
        assets_dir = self.assets_dir

        class Handler(_AvatarHandler):
            pass

        Handler.assets_dir = assets_dir
        self._httpd = ThreadingHTTPServer((self.host, self.port), Handler)
        self._thread = threading.Thread(
            target=self._httpd.serve_forever, name="AvatarServer", daemon=True
        )
        self._thread.start()
        log.info(f"Avatar HTTP-сервер: {self.url}")

    def stop(self) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None
            log.info("Avatar сервер остановлен.")