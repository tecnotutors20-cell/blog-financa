#!/usr/bin/env python3
import hashlib
import html as html_lib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

BLOG_ID = "6682336557114829830"
API_BASE = "https://www.googleapis.com/blogger/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"
ROOT = Path(__file__).resolve().parents[1]
COVER_DIR = ROOT / "assets" / "recipes-covers"
RESULT_FILE = ROOT / "recipes-site" / "cover-sync-result.txt"
RAW_BASE = "https://raw.githubusercontent.com/tecnotutors20-cell/blog-financa/main/assets/recipes-covers"
MARKER = "<!-- receitas-para-pequenos-cover -->"
W, H = 1200, 630

PALETTES = [
    ("#F7F1E8", "#36513A", "#D97B55", "#F3C969"),
    ("#FFF5EC", "#553C2B", "#E49A64", "#9CBF88"),
    ("#F0F5ED", "#2F4A34", "#A6C48A", "#E6B566"),
    ("#FFF2F0", "#5A3742", "#D7828F", "#E9B872"),
    ("#F4F3EE", "#334B52", "#7EB3A7", "#E7B96A"),
    ("#FFF8E6", "#4A4337", "#D7A34D", "#8DB184"),
]

ACCENT_BY_WORD = {
    "cenoura": "#E8873A", "abobora": "#E5933B", "abóbora": "#E5933B",
    "banana": "#E6C84E", "maca": "#D7655A", "maçã": "#D7655A",
    "morango": "#D85A67", "manga": "#E9A23B", "milho": "#E4C341",
    "brocolis": "#6F9F58", "brócolis": "#6F9F58", "espinafre": "#5F8F62",
    "ervilha": "#75A85A", "abobrinha": "#86A96C", "lentilha": "#B78154",
    "feijao": "#7A5139", "feijão": "#7A5139", "carne": "#A95B4D",
    "frango": "#D7A25B", "peixe": "#6F9FB7", "batata-doce": "#B36C66",
    "beterraba": "#A94A70", "coco": "#C6A782", "aveia": "#C9A96E",
    "pera": "#A7B96A", "tomate": "#D96350", "queijo": "#E5B85C",
}


def required_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Variável ausente: {name}")
    return value


def token():
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
            with urllib.request.urlopen(req, timeout=45) as r:
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


def hexrgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def fonts():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ]
    regulars = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    bold = next(x for x in candidates if Path(x).exists())
    reg = next(x for x in regulars if Path(x).exists())
    return (
        ImageFont.truetype(bold, 56),
        ImageFont.truetype(bold, 24),
        ImageFont.truetype(reg, 22),
    )


def wrap(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = word if not line else line + " " + word
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines[:4]


def keyword_accent(title, fallback):
    low = title.casefold()
    for key, color in ACCENT_BY_WORD.items():
        if key in low:
            return color
    return fallback


def draw_food_art(draw, idx, accent, secondary, bg):
    a, s, b = hexrgb(accent), hexrgb(secondary), hexrgb(bg)
    # Six varied editorial food compositions.
    if idx == 0:
        draw.ellipse((790, 95, 1145, 450), fill=(255, 255, 255), outline=a, width=10)
        draw.ellipse((835, 140, 1100, 405), fill=hexrgb(secondary))
        for x, y, r in [(900,210,42),(1000,225,36),(945,310,48)]:
            draw.ellipse((x-r,y-r,x+r,y+r), fill=a)
        draw.rounded_rectangle((875,465,1070,505), 20, fill=a)
    elif idx == 1:
        draw.rounded_rectangle((770, 120, 1135, 450), 55, fill=(255,255,255), outline=a, width=9)
        for i in range(5):
            x=820+i*60
            draw.ellipse((x,190+(i%2)*35,x+58,248+(i%2)*35), fill=a if i%2==0 else s)
        draw.arc((825,250,1085,410),0,180,fill=s,width=18)
    elif idx == 2:
        draw.ellipse((800,120,1120,440), fill=(255,255,255), outline=s, width=8)
        draw.pieslice((840,160,1080,400), 15, 120, fill=a)
        draw.pieslice((840,160,1080,400), 135, 230, fill=s)
        draw.pieslice((840,160,1080,400), 245, 345, fill=hexrgb("#E9C87B"))
        draw.line((780,490,1120,490), fill=a, width=18)
    elif idx == 3:
        for i,(x,y) in enumerate([(850,160),(995,145),(905,300),(1040,305)]):
            r=72 if i<2 else 64
            draw.ellipse((x-r,y-r,x+r,y+r), fill=a if i%2==0 else s)
            draw.ellipse((x-8,y-r-20,x+8,y-r+10), fill=hexrgb("#5E7E52"))
        draw.rounded_rectangle((800,450,1125,505), 26, fill=(255,255,255), outline=a, width=6)
    elif idx == 4:
        draw.rounded_rectangle((800,105,1125,430), 40, fill=s)
        for yy in (165,265,365):
            draw.rounded_rectangle((850,yy,1075,yy+45), 18, fill=a)
        draw.ellipse((1040,450,1100,510), fill=a)
        draw.line((1070,480,1135,545), fill=a, width=15)
    else:
        draw.ellipse((820,110,1115,405), fill=(255,255,255), outline=a, width=9)
        draw.arc((850,155,1085,390), 20, 160, fill=a, width=22)
        draw.arc((865,175,1070,370), 190, 340, fill=s, width=20)
        draw.line((820,480,1110,480), fill=s, width=14)
        draw.line((865,530,1065,530), fill=a, width=8)


def generate_cover(title, path):
    digest = hashlib.sha256(title.encode("utf-8")).digest()
    palette = PALETTES[digest[0] % len(PALETTES)]
    bg, dark, secondary, warm = palette
    accent = keyword_accent(title, warm)
    img = Image.new("RGB", (W, H), hexrgb(bg))
    d = ImageDraw.Draw(img)
    title_font, brand_font, small_font = fonts()

    # editorial frame and side accent
    d.rounded_rectangle((36,36,W-36,H-36), 36, outline=hexrgb(dark), width=3)
    d.rounded_rectangle((72,74,245,116), 21, fill=hexrgb(accent))
    d.text((94,82), "RECEITA", font=brand_font, fill=(255,255,255))
    d.text((74,145), "Receitas Para Pequenos", font=brand_font, fill=hexrgb(dark))

    lines = wrap(d, title, title_font, 650)
    y = 205
    for line in lines:
        d.text((72,y), line, font=title_font, fill=hexrgb(dark))
        y += 68

    d.text((74,548), "Receita prática • preparo passo a passo", font=small_font, fill=hexrgb(dark))
    draw_food_art(d, digest[1] % 6, accent, secondary, bg)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", quality=90, optimize=True, progressive=True)


def remove_old_leading_image(content):
    soup = BeautifulSoup(content or "", "html.parser")
    marker_found = MARKER in (content or "")
    if marker_found:
        return str(soup), False

    # Remove only the first image block when it appears before substantive recipe text.
    first_img = soup.find("img")
    if first_img:
        first_heading = soup.find(["h1", "h2", "h3"])
        if first_heading is None or first_img.sourceline is None or first_heading.sourceline is None or first_img.sourceline <= first_heading.sourceline:
            wrapper = first_img.find_parent("div", class_="separator") or first_img.find_parent("a")
            if wrapper:
                wrapper.decompose()
            else:
                first_img.decompose()
    return str(soup), True


def cover_html(title, url):
    alt = html_lib.escape(title, quote=True)
    return (
        MARKER
        + "<div class='separator' style='clear:both;margin:0 0 24px;text-align:center'>"
        + f"<img alt='{alt}' data-original-height='630' data-original-width='1200' "
        + f"src='{url}' style='border-radius:14px;height:auto;max-width:100%;width:1200px'/>"
        + "</div>"
    )


def main():
    tok = token()
    posts = live_posts(tok)
    generated = 0
    updated = 0
    skipped = 0
    failures = []

    for post in posts:
        post_id = str(post["id"])
        title = post.get("title") or "Receita para pequenos"
        filename = f"{post_id}.jpg"
        local = COVER_DIR / filename
        if not local.exists():
            generate_cover(title, local)
            generated += 1

    # Covers are committed by the workflow before this script is re-run with SYNC_BLOGGER=1.
    if os.environ.get("SYNC_BLOGGER") != "1":
        RESULT_FILE.write_text(f"phase=generated\nposts={len(posts)}\ngenerated={generated}\n", encoding="utf-8")
        return

    for post in posts:
        try:
            post_id = str(post["id"])
            title = post.get("title") or "Receita para pequenos"
            cover_url = f"{RAW_BASE}/{post_id}.jpg"
            content = post.get("content") or ""
            if MARKER in content and cover_url in content:
                skipped += 1
                continue
            cleaned, _ = remove_old_leading_image(content)
            # Strip any previous marker cover block before adding the canonical one.
            cleaned = re.sub(r"<!-- receitas-para-pequenos-cover -->\s*<div class=['\"]separator['\"].*?</div>", "", cleaned, count=1, flags=re.S)
            new_content = cover_html(title, cover_url) + cleaned
            payload = {"title": title, "content": new_content, "labels": post.get("labels") or []}
            api(tok, "PATCH", f"/blogs/{BLOG_ID}/posts/{post_id}", params={"publish": "true"}, body=payload)
            updated += 1
            time.sleep(2)
        except Exception as exc:
            failures.append(f"{post.get('id')}|{post.get('title')}|{type(exc).__name__}:{exc}")

    outcome = "success" if not failures and updated + skipped == len(posts) else "failed"
    lines = [
        f"outcome={outcome}", f"posts={len(posts)}", f"generated={generated}",
        f"updated={updated}", f"already_ok={skipped}", f"failures={len(failures)}"
    ] + ["failure=" + x for x in failures]
    RESULT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if outcome != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
