#!/usr/bin/env python3
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://www.googleapis.com/blogger/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ROOT = Path(__file__).resolve().parents[1]
PAGES_FILE = ROOT / "content" / "blogger_pages.json"
POSTS_FILE = ROOT / "content" / "blogger_posts.json"
WRITE_DELAY_SECONDS = 3.0
MAX_RETRIES = 7
COVER_BASE = "https://raw.githubusercontent.com/tecnotutors20-cell/blog-financa/main/assets/covers-real"
COVER_BY_TITLE = {
    "orçamento mensal: como organizar o dinheiro e saber quanto realmente sobra": f"{COVER_BASE}/orcamento-mensal-guia-20260828.svg",
    "dívida negociada pode voltar se eu atrasar o acordo? entenda o que acontece": f"{COVER_BASE}/divida-acordo-atrasado-20260827.svg",
    "vale a pena pegar empréstimo para pagar cartão de crédito? veja como comparar": f"{COVER_BASE}/emprestimo-pagar-cartao-20260827.svg",
    "renegociação de dívidas: como negociar sem trocar uma dívida por outra pior": f"{COVER_BASE}/renegociacao-dividas-guia-20260827.svg",
    "quanto tempo depois de pagar uma dívida o score pode mudar?": f"{COVER_BASE}/score-apos-pagar-divida-20260826.svg",
    "consultar o score várias vezes diminui a pontuação? entenda a diferença entre consulta própria e consulta de empresas": f"{COVER_BASE}/consultar-score-varias-vezes-20260826.svg",
    "score de crédito: como funciona, o que influencia e por que a aprovação não é garantida": f"{COVER_BASE}/score-credito-guia-20260826.svg",
    "pix agendado pode ser cancelado? veja quando ainda dá tempo": f"{COVER_BASE}/pix-seguranca.jpg",
    "med do pix: como pedir devolução após golpe e qual é o prazo?": f"{COVER_BASE}/pix-seguranca.jpg",
    "pagar a fatura antes do fechamento libera limite? entenda como funciona": "https://raw.githubusercontent.com/tecnotutors20-cell/blog-financa/main/assets/covers-real/pagar-fatura-antes-fechamento.svg",
    "como organizar a vida financeira do zero: um plano em 7 etapas": f"{COVER_BASE}/organizar-vida-financeira.jpg",
    "reserva de emergência: como calcular, montar e onde guardar": f"{COVER_BASE}/reserva-emergencia.jpg",
    "cartão de crédito: como funciona a fatura, o pagamento mínimo e os juros": f"{COVER_BASE}/cartao-credito.jpg",
    "score de crédito: o que influencia e como melhorar sem cair em promessas": f"{COVER_BASE}/score-credito.jpg",
    "conta digital ou banco tradicional: como escolher a melhor opção para você": f"{COVER_BASE}/conta-digital-banco.jpg",
    "renda fixa para iniciantes: 8 conceitos que você precisa entender antes de investir": f"{COVER_BASE}/renda-fixa.jpg",
    "como sair das dívidas: um método prático para priorizar e negociar": f"{COVER_BASE}/sair-das-dividas.jpg",
    "pix com segurança: cuidados para reduzir o risco de golpes e transferências erradas": f"{COVER_BASE}/pix-seguranca.jpg",
    "fechamento da fatura do cartão: como funciona e qual é o melhor dia para comprar?": f"{COVER_BASE}/cartao-credito.jpg",
    "compra feita no dia do fechamento do cartão cai em qual fatura?": f"{COVER_BASE}/cartao-credito.jpg",
}


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

    for attempt in range(MAX_RETRIES + 1):
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Authorization", f"Bearer {token}")
        request.add_header("Accept", "application/json")
        if body is not None:
            request.add_header("Content-Type", "application/json; charset=utf-8")

        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read()
                result = json.loads(raw.decode("utf-8")) if raw else {}
            if method in {"POST", "PATCH", "PUT", "DELETE"}:
                time.sleep(WRITE_DELAY_SECONDS)
            return result
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            retryable = exc.code in {429, 500, 502, 503, 504}
            if retryable and attempt < MAX_RETRIES:
                retry_after = exc.headers.get("Retry-After")
                if retry_after and retry_after.isdigit():
                    wait = max(int(retry_after), 5)
                else:
                    wait = min(5 * (2**attempt), 60)
                print(
                    f"Blogger API temporariamente limitada ({exc.code}); "
                    f"nova tentativa em {wait}s...",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue
            raise RuntimeError(
                f"Blogger API {method} {path} falhou ({exc.code}): {detail}"
            ) from exc

    raise RuntimeError(f"Blogger API {method} {path}: tentativas esgotadas")


def paginated_items(token: str, path: str, extra_params=None):
    items = []
    page_token = None
    while True:
        params = {"maxResults": 500, "fetchBodies": True, "view": "ADMIN"}
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


def editorial_author_box() -> str:
    return (
        "<!-- guia-do-bolso-author -->"
        "<aside class='guia-author-box' style='background:#f5f7f9;border:1px solid #e1e6ea;border-radius:10px;margin:0 0 24px;padding:14px 16px'>"
        "<strong>Por Equipe Editorial do Guia Do Bolso</strong>"
        "<p style='margin:6px 0 0'>Conteúdo educativo produzido com critérios editoriais, fontes confiáveis e transparência sobre o uso de tecnologia. "
        "<a href='/p/equipe-editorial.html'>Conheça nossa autoria e metodologia editorial</a>.</p>"
        "</aside>"
    )


def render_post_content(post: dict, blog_name: str) -> str:
    title = post["title"].strip()
    content = render(post["content"], blog_name)
    author_html = editorial_author_box()
    cover = COVER_BY_TITLE.get(title.casefold())
    if not cover:
        return author_html + content
    alt = html.escape(title, quote=True)
    cover_html = (
        "<!-- guia-do-bolso-cover -->"
        "<div class='separator' style='clear:both;margin:0 0 24px;text-align:center'>"
        f"<img alt='{alt}' data-original-height='630' data-original-width='1200' "
        f"src='{cover}' style='border-radius:12px;height:auto;max-width:100%;width:1200px'/>"
        "</div>"
    )
    return cover_html + author_html + content


POST_URL_PATTERN = re.compile(r"\{\{POST_URL\|(.+?)\}\}")

def resolve_post_urls(content: str, url_by_title: dict) -> str:
    def repl(match):
        title = match.group(1).strip().casefold()
        return html.escape(url_by_title.get(title, "#"), quote=True)
    return POST_URL_PATTERN.sub(repl, content)


def normalized_labels(labels):
    return sorted(str(label).strip().casefold() for label in (labels or []))


def upsert_pages(token: str, blog_id: str, blog_name: str):
    pages = json.loads(PAGES_FILE.read_text(encoding="utf-8"))
    existing = paginated_items(token, f"/blogs/{blog_id}/pages")
    by_title = {item.get("title", "").strip().casefold(): item for item in existing}

    for page in pages:
        title = page["title"].strip()
        rendered_content = render(page["content"], blog_name)
        payload = {"title": title, "content": rendered_content}
        current = by_title.get(title.casefold())
        if current:
            if (current.get("content") or "").strip() == rendered_content.strip():
                print(f"Página já está atualizada: {title}")
                continue
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
    url_by_title = {key: item.get("url", "#") for key, item in by_title.items()}

    for post in posts:
        title = post["title"].strip()
        rendered_content = resolve_post_urls(render_post_content(post, blog_name), url_by_title)
        labels = post.get("labels", [])
        payload = {
            "title": title,
            "content": rendered_content,
            "labels": labels,
        }
        current = by_title.get(title.casefold())
        if current:
            same_content = (current.get("content") or "").strip() == rendered_content.strip()
            same_labels = normalized_labels(current.get("labels")) == normalized_labels(labels)
            if same_content and same_labels:
                print(f"Post já está atualizado: {title}")
                continue
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
