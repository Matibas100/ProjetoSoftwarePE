"""Servidor local do frontend, independente da API e do diretório de trabalho."""

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


PUBLIC_ROOT = Path(__file__).resolve().parents[1] / "frontend"
PAGES = {"/login": "login.html", "/cadastro": "cadastro.html"}
ALIASES = {
    "/login.html": "/login",
    "/login/": "/login",
    "/cadastro.html": "/cadastro",
    "/cadastro/": "/cadastro",
}


class FrontendHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_ROOT), **kwargs)

    def translate_path(self, path):
        pathname = urlsplit(path).path
        return super().translate_path("/" + PAGES[pathname] if pathname in PAGES else path)

    def send_head(self):
        url = urlsplit(self.path)
        if ".." in unquote(url.path).replace("\\", "/").split("/"):
            self.send_error(404, "Arquivo não encontrado")
            return None
        if url.path in ALIASES:
            location = ALIASES[url.path]
            if url.query:
                location += "?" + url.query
            self.send_response(302)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return None

        # resolve também segue symlinks e junctions; índices de diretório
        # precisam da mesma contenção antes de o handler padrão abri-los.
        try:
            target = Path(self.translate_path(self.path))
            candidates = [target]
            if target.is_dir():
                candidates.extend(target / name for name in ("index.html", "index.htm"))
            if any(not path.resolve().is_relative_to(PUBLIC_ROOT.resolve()) for path in candidates):
                self.send_error(404, "Arquivo não encontrado")
                return None
        except (OSError, RuntimeError, ValueError):
            self.send_error(404, "Arquivo não encontrado")
            return None
        return super().send_head()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5500, help="Porta local (padrão: 5500)")
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), FrontendHandler) as server:
        print(f"Frontend: http://127.0.0.1:{server.server_port}/login", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
