#!/usr/bin/env python3
import hashlib
import html
import io
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

BLOG_ID = '6682336557114829830'
API = 'https://www.googleapis.com/blogger/v3'
TOKEN_URL = 'https://oauth2.googleapis.com/token'
ROOT = Path(__file__).resolve().parents[1]
COVER_DIR = ROOT / 'assets' / 'recipes-covers-ai-v2'
LOG_PATH = ROOT / 'recipes-site' / 'published_content_log.json'
RESULT_PATH = ROOT / 'recipes-site' / 'automation-publish-result.txt'
RAW_BASE = 'https://raw.githubusercontent.com/tecnotutors20-cell/blog-financa/main/assets/recipes-covers-ai-v2'
MARKER = '<!-- receitas-para-pequenos-ai-v2 -->'
TITLE = 'Purê de Abóbora com Carne para Bebê: Receita Cremosa e Fácil'
SLUG_KEY = 'pure-abobora-carne-bebe'
CLUSTER = 'Cluster 1 — Papinhas, purês, sopas e cremes'
W, H = 1200, 630


def env(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise RuntimeError('missing ' + name)
    return value


def token():
    data = urllib.parse.urlencode({
        'client_id': env('GOOGLE_CLIENT_ID'),
        'client_secret': env('GOOGLE_CLIENT_SECRET'),
        'refresh_token': env('GOOGLE_REFRESH_TOKEN'),
        'grant_type': 'refresh_token',
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)['access_token']


def api(tok, method, path, params=None, body=None):
    url = API + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode('utf-8')
    for attempt in range(6):
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header('Authorization', 'Bearer ' + tok)
        req.add_header('Accept', 'application/json')
        if body is not None:
            req.add_header('Content-Type', 'application/json; charset=utf-8')
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                raw = response.read()
                return json.loads(raw.decode()) if raw else {}
        except urllib.error.HTTPError as error:
            if error.code in {429, 500, 502, 503, 504} and attempt < 5:
                time.sleep(min(5 * (2 ** attempt), 45))
                continue
            raise


def list_posts(tok):
    items = []
    page = None
    while True:
        params = {'maxResults': 500, 'fetchBodies': True, 'status': 'LIVE', 'view': 'ADMIN'}
        if page:
            params['pageToken'] = page
        data = api(tok, 'GET', f'/blogs/{BLOG_ID}/posts', params)
        items.extend(data.get('items', []))
        page = data.get('nextPageToken')
        if not page:
            return items


def generate_cover(path):
    prompt = (
        "Photorealistic horizontal food photograph of the finished Brazilian baby-friendly recipe "
        "'Purê de Abóbora com Carne para Bebê'. Show a thick, spoonable pumpkin puree with finely crumbled "
        "well-cooked ground beef visibly mixed through it, warm orange pumpkin color, realistic homemade texture. "
        "Serve in a small shallow handmade neutral ceramic bowl on a light oak family dining table, soft natural morning "
        "window light, three-quarter editorial food photography, understated Brazilian home kitchen background blur. "
        "The puree must be thick rather than liquid, with fork-mashed texture and small soft beef granules. "
        "No baby, no child, no people, no hands. No text, no typography, no logo, no watermark, no packaging, no labels, "
        "no collage, no illustration, no cartoon. Natural food colors, realistic imperfections, professional recipe blog photography."
    )
    encoded = urllib.parse.quote(prompt, safe='')
    seed = int(hashlib.sha256(TITLE.encode()).hexdigest()[:12], 16) % 2147483647
    last_error = None
    for attempt in range(8):
        url = (
            f'https://image.pollinations.ai/prompt/{encoded}?width={W}&height={H}&model=flux&nologo=true&safe=true'
            f'&enhance=true&seed={seed + attempt * 10007}'
        )
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; ReceitasParaPequenos/3.0)',
                'Accept': 'image/*',
            })
            with urllib.request.urlopen(req, timeout=240) as response:
                raw = response.read()
            if len(raw) < 15000:
                raise RuntimeError('small image response')
            image = Image.open(io.BytesIO(raw)).convert('RGB')
            target_ratio = W / H
            current_ratio = image.width / image.height
            if current_ratio > target_ratio:
                new_width = int(image.height * target_ratio)
                x = (image.width - new_width) // 2
                image = image.crop((x, 0, x + new_width, image.height))
            elif current_ratio < target_ratio:
                new_height = int(image.width / target_ratio)
                y = (image.height - new_height) // 2
                image = image.crop((0, y, image.width, y + new_height))
            image = image.resize((W, H), Image.Resampling.LANCZOS)
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path, 'JPEG', quality=92, optimize=True, progressive=True)
            return
        except Exception as error:
            last_error = error
            time.sleep(min(10 * (attempt + 1), 45))
    raise RuntimeError(f'cover generation failed: {last_error}')


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, text=True, capture_output=True)


def git_commit_push(paths, message):
    git('config', 'user.name', 'github-actions[bot]')
    git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    git('add', *[str(Path(p).relative_to(ROOT)) for p in paths])
    commit = git('commit', '-m', message)
    if commit.returncode not in (0, 1):
        raise RuntimeError(commit.stderr)
    pull = git('pull', '--rebase', 'origin', 'main')
    if pull.returncode != 0:
        raise RuntimeError(pull.stderr)
    push = git('push', 'origin', 'main')
    if push.returncode != 0:
        raise RuntimeError(push.stderr)


def article_html(cover_url):
    schema = {
        '@context': 'https://schema.org',
        '@type': 'Recipe',
        'name': TITLE,
        'image': [cover_url],
        'author': {'@type': 'Organization', 'name': 'Equipe Editorial do Receitas Para Pequenos'},
        'description': 'Purê espesso de abóbora com carne moída bem cozida, com textura ajustável para a alimentação complementar.',
        'recipeCategory': 'Almoço e jantar',
        'recipeCuisine': 'Brasileira',
        'keywords': 'purê de abóbora com carne para bebê, alimentação complementar, papinha de abóbora com carne',
        'recipeYield': '2 porções pequenas',
        'recipeIngredient': [
            '200 g de abóbora cabotiá ou moranga, descascada e cortada em cubos',
            '100 g de carne bovina moída',
            '2 colheres (sopa) de cebola bem picada',
            'Água suficiente para o cozimento',
        ],
        'recipeInstructions': [
            {'@type': 'HowToStep', 'text': 'Cozinhe a abóbora em pouca água até ficar muito macia.'},
            {'@type': 'HowToStep', 'text': 'Em outra panela, cozinhe a carne moída com a cebola, mexendo e desfazendo os grumos, até ficar completamente cozida.'},
            {'@type': 'HowToStep', 'text': 'Amasse a abóbora com um garfo e ajuste a umidade com pequenas quantidades da água do cozimento.'},
            {'@type': 'HowToStep', 'text': 'Misture a carne bem desmanchada ao purê e adapte a textura às habilidades da criança.'},
        ],
    }
    schema_json = json.dumps(schema, ensure_ascii=False).replace('</', '<\\/')
    alt = html.escape(TITLE + ' - Receitas Para Pequenos', quote=True)
    return f"""{MARKER}
<div class='separator' style='clear:both;margin:0 0 24px;text-align:center'><img alt='{alt}' data-original-height='630' data-original-width='1200' src='{cover_url}' style='border-radius:14px;height:auto;max-width:100%;width:1200px'/></div>
<p><strong>Por Equipe Editorial do Receitas Para Pequenos</strong></p>
<p>Este purê de abóbora com carne é uma opção simples para o almoço ou jantar quando a criança já iniciou a alimentação complementar. A proposta é deixar a abóbora bem macia e a carne moída totalmente cozida e desmanchada, formando um preparo espesso que pode ser adaptado com o garfo conforme as habilidades da criança.</p>
<p><strong>Atenção:</strong> a textura e o formato devem ser adaptados às habilidades individuais, sempre com a criança sentada e supervisionada durante a refeição. Em caso de alergias, dificuldades de mastigação/deglutição ou necessidades especiais, procure orientação de profissional habilitado.</p>
<h2>Ingredientes</h2>
<ul>
<li>200 g de abóbora cabotiá ou moranga, descascada e cortada em cubos</li>
<li>100 g de carne bovina moída</li>
<li>2 colheres (sopa) de cebola bem picada</li>
<li>Água suficiente para o cozimento</li>
</ul>
<h2>Modo de preparo</h2>
<ol>
<li>Cozinhe a abóbora em pouca água até ficar muito macia e fácil de amassar com o garfo.</li>
<li>Enquanto isso, coloque a carne moída e a cebola em outra panela. Cozinhe em fogo médio, mexendo e desfazendo os grumos, até que a carne esteja completamente cozida.</li>
<li>Escorra a maior parte da água da abóbora, reservando um pouco. Amasse com o garfo até formar um purê espesso.</li>
<li>Misture a carne bem desmanchada ao purê. Se necessário, acrescente pequenas colheradas da água do cozimento para ajustar a consistência sem deixar o prato líquido.</li>
<li>Espere amornar e confira a textura antes de servir.</li>
</ol>
<h2>Como deve ficar a textura</h2>
<p>O resultado ideal é cremoso e espesso, permanecendo na colher sem escorrer como sopa. A carne deve estar em grânulos pequenos e macios, sem blocos compactos. O Ministério da Saúde orienta que, no início da alimentação complementar, os alimentos sejam oferecidos amassados e que a consistência evolua gradualmente, em vez de permanecer sempre liquidificada.</p>
<h2>Como servir e adaptar</h2>
<p>Para uma criança no começo da alimentação complementar, amasse a abóbora com bastante cuidado e desfaça muito bem os grumos da carne. Conforme ela desenvolve habilidades para lidar com texturas mais marcadas, deixe o purê menos uniforme. Não é necessário transformar tudo em líquido: a ideia é adaptar a consistência de forma progressiva.</p>
<p>O Ministério da Saúde informa que alimentos in natura ou minimamente processados podem ser oferecidos junto ao leite materno a partir dos 6 meses e recomenda comida amassada quando a criança começa a receber outros alimentos.</p>
<h2>Substituições culinárias</h2>
<p>A abóbora cabotiá pode ser trocada por moranga. Para variar o preparo, outra carne bovina moída pode ser usada desde que seja completamente cozida e fique com textura macia. Alterações para crianças com alergias ou necessidades específicas devem ser discutidas com profissional habilitado.</p>
<h2>Armazenamento</h2>
<p>Como a receita contém carne moída, não vamos indicar um prazo único de conservação sem contexto de temperatura e manipulação. Para reduzir risco, prepare porções pequenas, mantenha higiene no preparo e siga orientações oficiais de conservação de alimentos. Não guarde para outra refeição a porção que já teve contato com a colher ou a boca da criança.</p>
<h2>Perguntas frequentes</h2>
<h3>Precisa bater no liquidificador?</h3>
<p>Não. Amasse a abóbora com garfo e desmanche bem a carne. Isso permite controlar melhor a espessura e evoluir a textura gradualmente.</p>
<h3>Posso deixar a carne separada do purê?</h3>
<p>Sim. Misturar é uma opção prática, mas os componentes também podem ser oferecidos lado a lado, desde que a textura esteja adequada às habilidades da criança.</p>
<h3>O purê pode ficar bem ralo?</h3>
<p>Evite acrescentar água em excesso. Um preparo espesso facilita manter a comida na colher e permite perceber melhor a textura dos alimentos.</p>
<h2>Receitas relacionadas</h2>
<ul>
<li><a href='https://www.receitasparapequenos.site/2026/07/pure-de-feijao-com-abobora-para-bebes.html'>Purê de Feijão com Abóbora para Bebês</a></li>
<li><a href='https://www.receitasparapequenos.site/2026/07/sopa-creme-de-abobora-com-lentilha-para.html'>Sopa Creme de Abóbora com Lentilha para Bebês</a></li>
<li><a href='https://www.receitasparapequenos.site/2026/08/almondegas-de-carne-moida-com-legumes.html'>Almôndegas de Carne Moída com Legumes para Bebês</a></li>
</ul>
<h2>Referências oficiais</h2>
<ul>
<li><a href='https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-da-crianca/primeira-infancia/alimentacao-saudavel' rel='nofollow'>Ministério da Saúde — Alimentação saudável na primeira infância</a></li>
<li><a href='https://www.gov.br/saude/pt-br/composicao/saps/promocao-da-saude/guias-alimentares/publicacoes/guia_da_crianca_2019.pdf/view' rel='nofollow'>Ministério da Saúde — Guia Alimentar para Crianças Brasileiras Menores de 2 Anos</a></li>
</ul>
<script type='application/ld+json'>{schema_json}</script>
"""


def load_log():
    if not LOG_PATH.exists():
        return []
    try:
        data = json.loads(LOG_PATH.read_text(encoding='utf-8'))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def main():
    tok = token()
    posts = list_posts(tok)
    for post in posts:
        title = (post.get('title') or '').casefold()
        if title == TITLE.casefold() or ('purê de abóbora' in title and 'carne' in title):
            RESULT_PATH.write_text(f'outcome=skipped_duplicate\ntitle={post.get("title", "")}\nurl={post.get("url", "")}\n', encoding='utf-8')
            git_commit_push([RESULT_PATH], 'Record duplicate prevention for morning recipe')
            return

    suffix = hashlib.sha1(TITLE.encode('utf-8')).hexdigest()[:10]
    cover_path = COVER_DIR / f'{SLUG_KEY}-{suffix}.jpg'
    cover_url = f'{RAW_BASE}/{cover_path.name}'
    if not cover_path.exists():
        generate_cover(cover_path)
        git_commit_push([cover_path], 'Add unique AI food photo for pumpkin beef puree')
        time.sleep(8)

    content = article_html(cover_url)
    if MARKER not in content or cover_url not in content:
        raise RuntimeError('cover marker verification failed before publish')

    created = api(tok, 'POST', f'/blogs/{BLOG_ID}/posts', {'isDraft': 'false', 'fetchBody': 'true'}, {
        'kind': 'blogger#post',
        'blog': {'id': BLOG_ID},
        'title': TITLE,
        'content': content,
        'labels': ['Alimentação complementar', 'Papinhas e purês', 'Abóbora', 'Carne'],
    })
    post_id = str(created.get('id', ''))
    post_url = created.get('url', '')
    if not post_id:
        raise RuntimeError('Blogger did not return post id')

    verified = api(tok, 'GET', f'/blogs/{BLOG_ID}/posts/{post_id}', {'view': 'ADMIN'})
    verified_content = verified.get('content') or ''
    if MARKER not in verified_content or cover_url not in verified_content:
        raise RuntimeError('live Blogger post failed cover verification')

    log = load_log()
    log.append({
        'published_at': created.get('published'),
        'title': TITLE,
        'url': post_url,
        'post_id': post_id,
        'cluster': CLUSTER,
        'keyword': 'purê de abóbora com carne para bebê',
        'cover_url': cover_url,
        'marker': MARKER,
    })
    LOG_PATH.write_text(json.dumps(log, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    RESULT_PATH.write_text(
        'outcome=success\n'
        f'title={TITLE}\n'
        f'url={post_url}\n'
        f'post_id={post_id}\n'
        f'cluster={CLUSTER}\n'
        f'cover_url={cover_url}\n'
        'marker_verified=true\n',
        encoding='utf-8',
    )
    git_commit_push([LOG_PATH, RESULT_PATH], 'Record published pumpkin beef puree recipe')


if __name__ == '__main__':
    main()
