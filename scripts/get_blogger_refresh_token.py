#!/usr/bin/env python3
"""One-time helper to authorize Blogger API without sharing a Google password.

Requires a Google Cloud OAuth Desktop client. The script opens Google's consent
screen, receives the local callback and prints the refresh token plus the blogs
the authorized account can manage. Store the output as GitHub Actions secrets;
never commit credentials or tokens to the repository.
"""

import json
import os
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
BLOGGER_API = "https://www.googleapis.com/blogger/v3"
SCOPE = "https://www.googleapis.com/auth/blogger"


def required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Defina {name} antes de executar.")
    return value


def main() -> None:
    client_id = required("GOOGLE_CLIENT_ID")
    client_secret = required("GOOGLE_CLIENT_SECRET")
    state = secrets.token_urlsafe(24)
    result = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({key: values[0] for key, values in query.items() if values})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                "<h2>Autorização recebida.</h2><p>Você pode fechar esta aba e voltar ao terminal.</p>".encode("utf-8")
            )

        def log_message(self, *_args):
            return

    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_port
    redirect_uri = f"http://127.0.0.1:{port}/"

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    print("Abrindo a autorização oficial do Google no navegador...")
    if not webbrowser.open(url):
        print("Abra esta URL no navegador:\n" + url)

    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    thread.join(timeout=300)
    server.server_close()

    if result.get("state") != state:
        raise RuntimeError("Retorno OAuth inválido ou expirado.")
    if "error" in result:
        raise RuntimeError(f"Google recusou a autorização: {result['error']}")
    code = result.get("code")
    if not code:
        raise RuntimeError("Código de autorização não recebido.")

    token_payload = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
    ).encode()
    token_request = urllib.request.Request(TOKEN_URL, data=token_payload, method="POST")
    token_request.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(token_request, timeout=30) as response:
        tokens = json.load(response)

    refresh_token = tokens.get("refresh_token")
    access_token = tokens.get("access_token")
    if not refresh_token or not access_token:
        raise RuntimeError("O Google não retornou refresh token. Revogue o acesso anterior e execute novamente com consentimento.")

    req = urllib.request.Request(f"{BLOGGER_API}/users/self/blogs?fetchUserInfo=false&view=ADMIN")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as response:
        blogs = json.load(response).get("items", [])

    print("\n=== SALVE COMO SEGREDOS DO GITHUB; NÃO COMMITAR ===")
    print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
    print("\nBlogs disponíveis nesta conta:")
    for blog in blogs:
        print(f"- {blog.get('name')} | BLOGGER_BLOG_ID={blog.get('id')} | {blog.get('url')}")
    print("\nGOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET são os mesmos do cliente OAuth usado agora.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
