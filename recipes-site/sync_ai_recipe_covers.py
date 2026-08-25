#!/usr/bin/env python3
import concurrent.futures
import hashlib
import html
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

BLOG_ID = "6682336557114829830"
API_BASE = "https://www.googleapis.com/blogger/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ROOT = Path(__file__).resolve().parents[1]
COVER_DIR = ROOT / "assets" / "recipes-covers-ai"
RESULT_FILE = ROOT / "recipes-site" / "ai-cover-sync-result.txt"
RAW_BASE = "https://raw.githubusercontent.com/tecnotutors20-cell/blog-financa/main/assets/recipes-covers-ai"
NEW_MARKER = "<!-- receitas-para-pequenos-ai-cover -->"
OLD_MARKER = "<!-- receitas-para-pequenos-cover -->"
W, H = 1200, 630

SCENES = [
    "bright Scandinavian home kitchen, pale wood table, soft morning window light",
    "cozy Brazilian home kitchen, warm natural daylight, neutral ceramic plate",
    "minimal cream tabletop, soft side light, linen napkin, editorial food styling",
    "rustic light-wood table, gentle afternoon window light, simple handmade ceramic plate",
    "clean modern kitchen counter, diffused daylight, subtle green plant far in background",
    "warm beige dining table, natural window light, soft shadows, understated family kitchen",
    "white stone countertop, airy daylight, neutral tableware, clean magazine food photography",
    "light oak table, soft backlight, simple child-sized dish, realistic home-food presentation",
]

ANGLES = [
    "three-quarter close-up food photography",
    "overhead food photography",
    "45-degree editorial food photography",
    "close natural table-level food photography",
]

PLATING = [
    "small matte ceramic plate",
    "small shallow ceramic bowl",
    "simple child-sized divided plate",
    "small neutral stoneware plate",
]


def required_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Variável ausente: {name}")
    return value


def oauth_token():
    data = urllib.parse.urlencode({
        "client_id": required_env("GOOGLE_CLIENT_ID"),
        "client_secret": required_env("GOOGLE_CLIENT_SECRET"),
        "refresh_token": required_env("GOOGLE_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["access_token"]


def api(tok, method, path, params=None, body=None):
    url = API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    for attempt in range(7):
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {tok}")
        req.add_header("Accept", "application/json")
        if body is not None:
            req.add_header("Content-Type", "application/json; charset=utf-8")
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                return json.loads(raw.decode("utf-8")) if raw else {}
        except urllib.error.HTTPError as exc:
            if exc.code in {429, 500, 502, 503, 504} and attempt < 6:
                time.sleep(min(5 * (2 ** attempt), 60))
                continue
            raise


def live_posts(tok):
    out, page = [], None
    while True:
        params = {"maxResults": 500, "fetchBodies": True, "status": "LIVE", "view": "ADMIN"}
        if page:
            params["pageToken"] = page
        data = api(tok, "GET", f"/blogs/{BLOG_ID}/posts", params=params)
        out.extend(data.get("items", []))
        page = data.get("nextPageToken")
        if not page:
            return out


def prompt_for(title, post_id, attempt=0):
    digest = hashlib.sha256((post_id + title).encode("utf-8")).digest()
    scene = SCENES[digest[0] % len(SCENES)]
    angle = ANGLES[digest[1] % len(ANGLES)]
    plating = PLATING[digest[2] % len(PLATING)]
    variant = digest[3] % 5
    return (
        "Photorealistic editorial food photograph of the FINISHED DISH described by this Brazilian Portuguese recipe title: "
        f"'{title}'. The actual cooked food must visually match the recipe name and its main ingredients. "
        "Make it look homemade, appetizing and believable, not luxury restaurant food. "
        "Baby/toddler-friendly presentation with soft-looking texture where appropriate, but no baby and no people in frame. "
        f"Serve it on a {plating}. Composition: {angle}. Setting: {scene}. "
        f"Visual variation number {variant + attempt}. Natural food colors, realistic imperfections, shallow depth of field when appropriate. "
        "No words, no typography, no labels, no logos, no watermark, no packages, no hands, no cutlery blocking the food. "
        "Horizontal blog hero image, professional recipe website photography, 1200x630 aspect ratio."
    )


def generation_url(title, post_id, attempt):
    prompt = urllib.parse.quote(prompt_for(title, post_id, attempt), safe="")
    seed_base = int(hashlib.sha256((post_id + title).encode()).hexdigest()[:12], 16)
    seed = (seed_base + attempt * 7919) % 2147483647
    return (
        f"https://image.pollinations.ai/prompt/{prompt}"
        f"?width={W}&height={H}&model=flux&nologo=true&safe=true&enhance=true&seed={seed}"
    )


def download_ai_cover(title, post_id, path):
    last = None
    for attempt in range(6):
        try:
            url = generation_url(title, post_id, attempt)
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ReceitasParaPequenosCoverBot/1.0)",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            })
            with urllib.request.urlopen(req, timeout=210) as r:
                raw = r.read()
            if len(raw) < 15000:
                raise RuntimeError(f"imagem pequena demais: {len(raw)} bytes")
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            if im.width < 700 or im.height < 350:
                raise RuntimeError(f"dimensões inesperadas: {im.size}")
            target_ratio = W / H
            ratio = im.width / im.height
            if ratio > target_ratio:
                new_w = int(im.height * target_ratio)
                left = (im.width - new_w) // 2
                im = im.crop((left, 0, left + new_w, im.height))
            elif ratio < target_ratio:
                new_h = int(im.width / target_ratio)
                top = (im.height - new_h) // 2
                im = im.crop((0, top, im.width, top + new_h))
            im = im.resize((W, H), Image.Resampling.LANCZOS)
            path.parent.mkdir(parents=True, exist_ok=True)
            im.save(path, "JPEG", quality=91, optimize=True, progressive=True)
            return
        except Exception as exc:
            last = exc
            time.sleep(min(7 * (attempt + 1), 35))
    raise RuntimeError(f"falha ao gerar {title}: {last}")


def remove_cover_blocks(content):
    text = content or ""
    # Remove our former template cover and any AI cover block so we can insert the canonical current one.
    for marker in (NEW_MARKER, OLD_MARKER):
        text = re.sub(
            re.escape(marker) + r"\s*<div[^>]*class=['\"]separator['\"][^>]*>.*?</div>",
            "",
            text,
            count=1,
            flags=re.I | re.S,
        )
    # Remove a leading legacy image block from old Blogger content, but leave recipe-body images intact.
    text = re.sub(
        r"^\s*(?:<div[^>]*class=['\"]separator['\"][^>]*>\s*)?(?:<a[^>]*>\s*)?<img\b[^>]*>(?:\s*</a>)?(?:\s*</div>)?",
        "",
        text,
        count=1,
        flags=re.I | re.S,
    )
    return text.lstrip()


def cover_html(title, url):
    alt = html.escape(f"{title} - Receitas Para Pequenos", quote=True)
    return (
        NEW_MARKER
        + "<div class='separator' style='clear:both;margin:0 0 24px;text-align:center'>"
        + f"<img alt='{alt}' data-original-height='630' data-original-width='1200' "
        + f"src='{url}' style='border-radius:14px;height:auto;max-width:100%;width:1200px'/>"
        + "</div>"
    )


def main():
    tok = oauth_token()
    posts = live_posts(tok)
    force = os.environ.get("FORCE_REGENERATE") == "1"
    sync = os.environ.get("SYNC_BLOGGER") == "1"
    generated, skipped_generation = 0, 0
    gen_failures = []

    jobs = []
    for p in posts:
        post_id = str(p["id"])
        title = p.get("title") or "Receita para pequenos"
        path = COVER_DIR / f"{post_id}.jpg"
        if force or not path.exists():
            jobs.append((title, post_id, path))
        else:
            skipped_generation += 1

    if jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            future_map = {pool.submit(download_ai_cover, t, i, p): (t, i) for t, i, p in jobs}
            for fut in concurrent.futures.as_completed(future_map):
                title, post_id = future_map[fut]
                try:
                    fut.result()
                    generated += 1
                except Exception as exc:
                    gen_failures.append(f"{post_id}|{title}|{type(exc).__name__}:{exc}")

    if gen_failures:
        lines = [
            "outcome=failed", "phase=generation", f"posts={len(posts)}", f"generated={generated}",
            f"generation_failures={len(gen_failures)}"
        ] + ["failure=" + x for x in gen_failures]
        RESULT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
        raise SystemExit(1)

    if not sync:
        RESULT_FILE.write_text(
            f"outcome=success\nphase=generated\nposts={len(posts)}\ngenerated={generated}\nalready_generated={skipped_generation}\n",
            encoding="utf-8",
        )
        return

    updated = 0
    already_ok = 0
    sync_failures = []
    for p in posts:
        try:
            post_id = str(p["id"])
            title = p.get("title") or "Receita para pequenos"
            cover_url = f"{RAW_BASE}/{post_id}.jpg"
            content = p.get("content") or ""
            if NEW_MARKER in content and cover_url in content:
                already_ok += 1
                continue
            new_content = cover_html(title, cover_url) + remove_cover_blocks(content)
            payload = {"title": title, "content": new_content, "labels": p.get("labels") or []}
            api(tok, "PATCH", f"/blogs/{BLOG_ID}/posts/{post_id}", params={"publish": "true"}, body=payload)
            updated += 1
            time.sleep(1.6)
        except Exception as exc:
            sync_failures.append(f"{p.get('id')}|{p.get('title')}|{type(exc).__name__}:{exc}")

    outcome = "success" if not sync_failures and updated + already_ok == len(posts) else "failed"
    lines = [
        f"outcome={outcome}", "phase=synced", f"posts={len(posts)}", f"generated={generated}",
        f"updated={updated}", f"already_ok={already_ok}", f"failures={len(sync_failures)}",
    ] + ["failure=" + x for x in sync_failures]
    RESULT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if outcome != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
