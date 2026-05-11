from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import mimetypes

hostName = "localhost"
serverPort = 8080
contacts_html = 'contacts.html'
static_dir = "static"


class MyServer(BaseHTTPRequestHandler):
    """
    Обработчик GET/POST.
    """

    def do_GET(self):
        """Обработка GET‑запросов."""
        if self._is_static_request(self.path):
            self._serve_static()
            return

        if self.path == "/":
            self._serve_contacts()
            return

        self.send_response(404)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("Страница не найдена".encode("utf-8"))

    def _is_static_request(self, path: str) -> bool:
        """True, если путь начинается с /static/ и файл существует."""
        if not path.startswith("/static/"):
            return False
        rel_path = path[len("/static/"):]          # часть после /static/
        safe_path = os.path.normpath(os.path.join(static_dir, rel_path))
        if not safe_path.startswith(static_dir):
            return False
        # Проверяем, что файл существует
        return os.path.isfile(safe_path)

    def _serve_static(self):
        """Отдаёт файл из static/, устанавливая правильный Content‑Type."""
        rel_path = self.path[len("/static/"):]    # путь после /static/
        file_path = os.path.normpath(os.path.join(static_dir, rel_path))

        if not file_path.startswith(static_dir):
            self._send_404()
            return

        if not os.path.isfile(file_path):
            self._send_404()
            return

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        with open(file_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
        self.end_headers()
        self.wfile.write(content)

    def _serve_contacts(self):
        """Отдаёт файл contacts.html (или index.html)."""
        if not os.path.isfile(contacts_html):
            self.send_response(404)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("Страница не найдена".encode("utf-8"))
            return

        with open(contacts_html, "r", encoding="utf-8") as f:
            html = f.read()

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


    def do_POST(self):
        """Обработка POST‑запросов."""
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")

        print("\n--- ПОЛУЧЕННЫЕ ДАННЫЕ ---")
        print(post_data)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Данные получены!\n".encode("utf-8"))

    def _send_404(self):
        """Универсальная отправка 404‑ответа."""
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("404 Not Found".encode("utf-8"))

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user.")
    finally:
        webServer.server_close()
        print("Server stopped.")
