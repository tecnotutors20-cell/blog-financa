#!/usr/bin/env python3
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://www.googleapis.com/blogger/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ROOT = Path(__file__).resolve().parents[1]
PAGES_FILE = ROOT / "content" / "blogger_pages.json"
POSTS_FILE = ROOT / "content" / "blogger_posts.json"


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Variável obrigatória ausente: {name}")
    return value


def refresh_access_token() -> str:
    payload = urllib.parse.urlencode(
        {
            "client_id": required_env("GOOGLE_CLIENT_ID"),
            "client_secret": required_env("GOOGLE_CLIENT_SECRET"),
            "refresh_token": required_env("GOOGLE_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        }
    ).encode()
    request = urllib.request.Request(TOKEN_URL, data=payload, method="POST")
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    return data["access_token"]


def api_request(token: str, method: str, path: str, params=None, body=None):
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Authorization", f"Bearer {token}")
    request.add_header("Accept", "application/json")
    if body is not None:
        request.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Blogger API {method} {path} falhou ({exc.code}): {detail}") from exc


def paginated_items(token: str, path: str, extra_params=None):
    items = []
    page_token = None
    while True:
        params = {"maxResults": 500, "fetchBodies": False, "view": "ADMIN"}
        if extra_params:
            params.update(extra_params)
        if page_token:
            params["pageToken"] = page_token
        data = api_request(token, "GET", path, params=params)
        items.extend(data.get("items", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            return items


def render(text: str, blog_name: str) -> str:
    return text.replace("{{BLOG_NAME}}", blog_name)


def upsert_pages(token: str, blog_id: str, blog_name: str):
    pages = json.loads(PAGES_FILE.read_text(encoding="utf-8"))
    existing = paginated_items(token, f"/blogs/{blog_id}/pages")
    by_title = {item.get("title", "").strip().casefold(): item for item in existing}

    for page in pages:
        title = page["title"].strip()
        payload = {"title": title, "content": render(page["content"], blog_name)}
        current = by_title.get(title.casefold())
        if current:
            page_id = current["id"]
            api_request(
                token,
                "PATCH",
                f"/blogs/{blog_id}/pages/{page_id}",
                params={"publish": "true"},
                body=payload,
            )
            print(f"Página atualizada/publicada: {title}")
        else:
            api_request(
                token,
                "POST",
                f"/blogs/{blog_id}/pages",
                params={"isDraft": "false"},
                body=payload,
            )
            print(f"Página criada/publicada: {title}")


def load_all_posts(token: str, blog_id: str):
    found = {}
    for status in ("LIVE", "DRAFT", "SCHEDULED"):
        try:
            items = paginated_items(token, f"/blogs/{blog_id}/posts", {"status": status})
        except RuntimeError:
            if status == "SCHEDULED":
                continue
            raise
        for item in items:
            found[item["id"]] = item
    return list(found.values())


def upsert_posts(token: str, blog_id: str, blog_name: str):
    posts = json.loads(POSTS_FILE.read_text(encoding="utf-8"))
    existing = load_all_posts(token, blog_id)
    by_title = {item.get("title", "").strip().casefold(): item for item in existing}

    for post in posts:
        title = post["title"].strip()
        payload = {
            "title": title,
            "content": render(post["content"], blog_name),
            "labels": post.get("labels", []),
        }
        current = by_title.get(title.casefold())
        if current:
            post_id = current["id"]
            api_request(
                token,
                "PATCH",
                f"/blogs/{blog_id}/posts/{post_id}",
                params={"publish": "true", "fetchBody": "false"},
                body=payload,
            )
            print(f"Post atualizado/publicado: {title}")
        else:
            api_request(
                token,
                "POST",
                f"/blogs/{blog_id}/posts",
                params={"isDraft": "false", "fetchBody": "false"},
                body=payload,
            )
            print(f"Post criado/publicado: {title}")


def main():
    blog_id = required_env("BLOGGER_BLOG_ID")
    token = refresh_access_token()
    blog = api_request(token, "GET", f"/blogs/{blog_id}", params={"view": "ADMIN"})
    blog_name = blog.get("name") or "este site"
    print(f"Destino confirmado: {blog_name} ({blog_id})")

    upsert_pages(token, blog_id, blog_name)
    upsert_posts(token, blog_id, blog_name)
    print("Publicação concluída.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
