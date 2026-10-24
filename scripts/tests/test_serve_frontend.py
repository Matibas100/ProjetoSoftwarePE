"""Contrato HTTP real do servidor local, sem API, segredos ou banco."""

from html.parser import HTMLParser
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
import re
from queue import Queue
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from serve_frontend import FrontendHandler, PUBLIC_ROOT


class QuietHandler(FrontendHandler):
    def log_message(self, *_args):
        pass


class PageResources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "img"}:
            self.resources.append(attrs["src"])
        elif tag == "link" and attrs.get("rel") == "stylesheet":
            self.resources.append(attrs["href"])
        elif tag == "a":
            self.links.append(attrs["href"])


class FrontendHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, path, method="GET", port=None):
        connection = HTTPConnection("127.0.0.1", port or self.server.server_port, timeout=5)
        try:
            connection.request(method, path)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_canonical_pages_direct_reload_query_and_head(self):
        for route, filename in (("/login", "login.html"), ("/cadastro", "cadastro.html")):
            for query in ("", "?origem=local&next=https%3A%2F%2Fexample.com"):
                with self.subTest(route=route, query=query):
                    status, headers, body = self.request(route + query)
                    self.assertEqual(status, 200)
                    self.assertEqual(headers["Content-type"], "text/html")
                    self.assertNotIn("Location", headers)
                    self.assertEqual(body, (PUBLIC_ROOT / filename).read_bytes())
                    self.assertEqual(self.request(route + query)[2], body)
                    head_status, head_headers, head_body = self.request(route + query, "HEAD")
                    self.assertEqual(head_status, status)
                    self.assertEqual(head_body, b"")
                    for header in ("Content-type", "Content-Length", "Last-Modified"):
                        self.assertEqual(head_headers[header], headers[header])

    def test_aliases_preserve_queries_with_fixed_local_destinations(self):
        for canonical in ("/login", "/cadastro"):
            for alias in (canonical + ".html", canonical + "/"):
                for query in ("", "?origem=local", "?next=https://example.com&redirect=//example.com"):
                    for method in ("GET", "HEAD"):
                        with self.subTest(alias=alias, query=query, method=method):
                            status, headers, body = self.request(alias + query, method)
                            self.assertEqual(status, 302)
                            self.assertEqual(headers["Location"], canonical + query)
                            self.assertEqual(headers["Content-Length"], "0")
                            self.assertEqual(body, b"")
                            final_status, final_headers, _ = self.request(headers["Location"], method)
                            self.assertEqual(final_status, 200)
                            self.assertNotIn("Location", final_headers)

    def test_legacy_pages_and_root(self):
        for route in ("/", "/index.html", "/aluno/inicio.html", "/admin/materias.html", "/admin/assuntos.html"):
            with self.subTest(route=route):
                status, headers, body = self.request(route)
                self.assertEqual(status, 200)
                self.assertEqual(headers["Content-type"], "text/html")
                self.assertEqual(body, (PUBLIC_ROOT / (route.lstrip("/") or "index.html")).read_bytes())

    def test_public_links_resources_and_css_fonts(self):
        for route, other in (("/login", "/cadastro"), ("/cadastro", "/login")):
            page = PageResources()
            page.feed(self.request(route)[2].decode("utf-8"))
            self.assertEqual(page.links, [other])
            self.assertEqual(page.resources, [
                "/css/auth.css", "/assets/logo-plataforma-enem-horizontal.svg",
                "/js/api.js", "/js/auth-session.js", "/js/auth-page.js",
            ])
            for resource in page.resources:
                with self.subTest(route=route, resource=resource):
                    status, headers, body = self.request(resource)
                    self.assertEqual(status, 200)
                    self.assertEqual(body, (PUBLIC_ROOT / resource.lstrip("/")).read_bytes())
                    self.assertNotEqual(headers["Content-type"], "text/html")
                    if resource.endswith(".css"):
                        self.assertEqual(headers["Content-type"], "text/css")
                        fonts = re.findall(r'url\([\'"]?([^\)\'\"]+)', body.decode("utf-8"))
                        self.assertTrue(fonts)
                        for font in fonts:
                            self.assertEqual(self.request(urljoin(resource, font))[0], 200)

    def test_unknown_api_and_external_paths_have_no_fallback(self):
        for route in (
            "/pagina-inexistente", "/login/inexistente", "/cadastro/inexistente",
            "/css/inexistente.css", "/api/auth/login", "/README.md", "/backend/run.py",
            "/../README.md", "/%2e%2e/README.md", "/%2e%2e%2fREADME.md",
            "/..%5cREADME.md", "/css/../../README.md",
        ):
            for method in ("GET", "HEAD"):
                with self.subTest(route=route, method=method):
                    status, headers, body = self.request(route, method)
                    self.assertEqual(status, 404)
                    self.assertNotIn("Location", headers)
                    self.assertNotIn(b'id="auth-form"', body)
                    if method == "HEAD":
                        self.assertEqual(body, b"")

    def test_junction_or_symlink_cannot_escape_public_root(self):
        with tempfile.TemporaryDirectory() as external, tempfile.TemporaryDirectory(dir=PUBLIC_ROOT) as public:
            external_path = Path(external)
            (external_path / "index.html").write_text("sentinela externa", encoding="utf-8")
            link = Path(public) / "outside"
            try:
                link.symlink_to(external_path, target_is_directory=True)
            except OSError:
                if sys.platform != "win32":
                    raise
                subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(external_path)],
                               check=True, capture_output=True)
            try:
                base = "/" + Path(public).name + "/outside"
                for route in (base, base + "/", base + "/index.html"):
                    for method in ("GET", "HEAD"):
                        status, _, body = self.request(route, method)
                        self.assertEqual(status, 404)
                        self.assertNotIn(b"sentinela externa", body)
            finally:
                if link.is_symlink():
                    link.unlink()
                else:
                    link.rmdir()  # Remove somente a junction; não percorre o destino.

    def test_cli_from_another_directory(self):
        script = PUBLIC_ROOT.parent / "scripts" / "serve_frontend.py"
        with tempfile.TemporaryDirectory() as working_dir:
            process = subprocess.Popen([sys.executable, str(script), "--port", "0"],
                                       cwd=working_dir, stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL, text=True)
            try:
                lines = Queue()
                reader = threading.Thread(target=lambda: lines.put(process.stdout.readline()), daemon=True)
                reader.start()
                output = lines.get(timeout=5)
                match = re.fullmatch(r"Frontend: http://127\.0\.0\.1:(\d+)/login\n", output)
                self.assertIsNotNone(match)
                self.assertEqual(self.request("/login", port=int(match[1]))[2],
                                 (PUBLIC_ROOT / "login.html").read_bytes())
            finally:
                process.terminate()
                process.wait(timeout=5)
                reader.join(timeout=5)
                process.stdout.close()


if __name__ == "__main__":
    unittest.main()
